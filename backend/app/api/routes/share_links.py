from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep, get_current_user
from app.models import Board, BoardRead, ShareLink, ShareLinkCreate, ShareLinkRead, User

router = APIRouter()


def _get_board_or_404(session: SessionDep, board_id: int) -> Board:
	board = session.get(Board, board_id)
	if board is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
	return board


@router.post("/boards/{board_id}/share-links", response_model=ShareLinkRead)
def create_share_link(
	session: SessionDep,
	board_id: int,
	payload: ShareLinkCreate,
	user: User = Depends(get_current_user),
) -> ShareLinkRead:
	board = _get_board_or_404(session, board_id)
	_ = payload
	expires_at = datetime.now(timezone.utc) + timedelta(days=1)
	share = ShareLink(
		token=secrets.token_urlsafe(32), board_id=board.id, expires_at=expires_at
	)
	session.add(share)
	session.commit()
	session.refresh(share)
	return ShareLinkRead(token=share.token, board_id=share.board_id, expires_at=share.expires_at)


@router.get("/boards/{board_id}/share-links", response_model=list[ShareLinkRead])
def list_share_links(
	session: SessionDep, board_id: int, user: User = Depends(get_current_user)
) -> list[ShareLinkRead]:
	_get_board_or_404(session, board_id)
	shares = session.exec(
		select(ShareLink).where(ShareLink.board_id == board_id)
	).all()
	return [ShareLinkRead.model_validate(share) for share in shares]


@router.delete("/share-links/{token}", status_code=status.HTTP_200_OK)
def delete_share_link(
	session: SessionDep, token: str, user: User = Depends(get_current_user)
) -> None:
	share = session.get(ShareLink, token)
	if share is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found")
	session.delete(share)
	session.commit()


@router.get("/share-links/{token}/board", response_model=BoardRead)
def resolve_share_link(session: SessionDep, token: str) -> BoardRead:
	share = session.get(ShareLink, token)
	if share is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found")
	expires_at = share.expires_at
	if expires_at.tzinfo is None:
		expires_at = expires_at.replace(tzinfo=timezone.utc)
	if expires_at < datetime.now(timezone.utc):
		raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share link expired")
	board = _get_board_or_404(session, share.board_id)
	return BoardRead.model_validate(board)
