from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.config import settings
from app.core.db import get_session
from app.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
	tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False
)

SessionDep = Annotated[Session, Depends(get_session)]


def _decode_token(token: str, expected_type: str) -> dict:
	try:
		payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
	except jwt.PyJWTError as exc:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token",
		) from exc

	if payload.get("type") != expected_type:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token type",
		)

	exp = payload.get("exp")
	if exp is not None and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(
		timezone.utc
	):
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Token expired",
		)

	return payload


def get_current_user(
	session: SessionDep, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
	payload = _decode_token(token, expected_type="access")
	user_id = payload.get("sub")
	if user_id is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Invalid token subject",
		)

	user = session.get(User, int(user_id))
	if user is None:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="User not found",
		)
	return user


def get_optional_user(
	session: SessionDep,
	token: Annotated[str | None, Depends(oauth2_scheme_optional)] = None,
) -> User | None:
	if not token:
		return None
	try:
		payload = _decode_token(token, expected_type="access")
		user_id = payload.get("sub")
		if user_id is None:
			return None
		return session.get(User, int(user_id))
	except HTTPException:
		return None


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
	if current_user.role != UserRole.ADMIN:
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Admin privileges required",
		)
	return current_user


def get_refresh_token_cookie(refresh_token: str | None = Cookie(default=None)) -> str:
	if not refresh_token:
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Missing refresh token",
		)
	return refresh_token
