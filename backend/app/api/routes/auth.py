from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app.api.deps import SessionDep, get_refresh_token_cookie
from app.core.config import settings
from app.core.security import (
	create_access_token,
	create_refresh_token,
	hash_token,
	verify_password,
)
from app.models import RefreshSession, Token, User

router = APIRouter(prefix="/auth")


def _decode_refresh_token(token: str) -> dict:
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
	except jwt.PyJWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
		) from exc

	if payload.get("type") != "refresh":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
		)
	return payload


def _set_refresh_cookie(response: Response, refresh_token: str) -> None:
	max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
	response.set_cookie(
		key="refresh_token",
		value=refresh_token,
		httponly=True,
		samesite="lax",
		max_age=max_age,
		path=f"{settings.API_V1_STR}/auth",
	)


@router.post("/login", response_model=Token)
def login(
	session: SessionDep,
	response: Response,
	form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
	user = session.exec(select(User).where(User.username == form_data.username)).first()
	if user is None:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
		)

	valid, new_hash = verify_password(form_data.password, user.password_hash)
	if not valid:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
		)
	if new_hash:
		user.password_hash = new_hash
		session.add(user)
		session.commit()

	access_token = create_access_token(
		user.id, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	)
	refresh_token = create_refresh_token(
		user.id, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
	)
	expires_at = datetime.now(timezone.utc) + timedelta(
		days=settings.REFRESH_TOKEN_EXPIRE_DAYS
	)
	session.add(
		RefreshSession(
			user_id=user.id,
			token_hash=hash_token(refresh_token),
			expires_at=expires_at,
		)
	)
	session.commit()

	_set_refresh_cookie(response, refresh_token)
	return Token(access_token=access_token)


@router.post("/refresh", response_model=Token)
def refresh_token(
	session: SessionDep,
	response: Response,
	refresh_token: str = Depends(get_refresh_token_cookie),
) -> Token:
	payload = _decode_refresh_token(refresh_token)
	user_id = payload.get("sub")
	if user_id is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
		)

	token_hash = hash_token(refresh_token)
	stored = session.exec(
		select(RefreshSession).where(
			RefreshSession.user_id == int(user_id),
			RefreshSession.token_hash == token_hash,
			RefreshSession.revoked_at.is_(None),
		)
	).first()
	if stored is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
		)
	expires_at = stored.expires_at
	if expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)
	if expires_at < datetime.now(timezone.utc):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
		)

	stored.revoked_at = datetime.now(timezone.utc)
	session.add(stored)

	access_token = create_access_token(
		int(user_id), timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
	)
	new_refresh_token = create_refresh_token(
		int(user_id), timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
	)
	expires_at = datetime.now(timezone.utc) + timedelta(
		days=settings.REFRESH_TOKEN_EXPIRE_DAYS
	)
	session.add(
		RefreshSession(
			user_id=int(user_id),
			token_hash=hash_token(new_refresh_token),
			expires_at=expires_at,
		)
	)
	session.commit()

	_set_refresh_cookie(response, new_refresh_token)
	return Token(access_token=access_token)


@router.post("/logout")
def logout(
	session: SessionDep,
	response: Response,
	refresh_token: str | None = Cookie(default=None),
) -> dict:
	if refresh_token:
		token_hash = hash_token(refresh_token)
		stored = session.exec(
			select(RefreshSession).where(RefreshSession.token_hash == token_hash)
		).first()
		if stored is not None and stored.revoked_at is None:
			stored.revoked_at = datetime.now(timezone.utc)
			session.add(stored)
			session.commit()

	response.delete_cookie(key="refresh_token", path=f"{settings.API_V1_STR}/auth")
	return {"status": "ok"}
