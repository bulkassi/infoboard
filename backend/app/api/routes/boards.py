from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlmodel import delete, select

from app.api.deps import SessionDep, get_current_user, get_optional_user
from app.models import (
    Board,
    BoardAbout,
    BoardAboutRead,
    BoardAboutUpdate,
    BoardCreate,
    BoardRead,
    BoardType,
    BoardUpdate,
    ShareLink,
    TagToCard,
    CardCommon,
    CardEmployee,
    CardService,
    User,
)

router = APIRouter(prefix="/boards")

PUBLIC_TYPES = {
    BoardType.MAIN,
    BoardType.ABOUT,
    BoardType.EMPLOYEES,
    BoardType.SERVICES,
}


def _get_board_or_404(session: SessionDep, board_id: int) -> Board:
    board = session.get(Board, board_id)
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


def _is_share_token_valid(
    session: SessionDep, board_id: int, token: str | None
) -> bool:
    if not token:
        return False
    share = session.exec(
        select(ShareLink).where(ShareLink.token == token, ShareLink.board_id == board_id)
    ).first()
    if share is None:
        return False
    return share.expires_at >= datetime.now(timezone.utc)


def _ensure_can_view_board(
    session: SessionDep, board: Board, user: User | None, share_token: str | None
) -> None:
    if board.type in PUBLIC_TYPES:
        return
    if user is not None:
        return
    if _is_share_token_valid(session, board.id, share_token):
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


@router.get("/", response_model=list[BoardRead])
def get_boards(session: SessionDep, user: User | None = Depends(get_optional_user)) -> Any:
    if user is None:
        boards = session.exec(select(Board).where(Board.type.in_(PUBLIC_TYPES))).all()
    else:
        boards = session.exec(select(Board)).all()
    return [BoardRead.model_validate(board) for board in boards]


@router.post("/", response_model=BoardRead, status_code=status.HTTP_201_CREATED)
def create_board(
    session: SessionDep, payload: BoardCreate, user: User = Depends(get_current_user)
) -> Any:
    board = Board(name=payload.name, type=BoardType.COMMON, owner_id=user.id)
    session.add(board)
    session.commit()
    session.refresh(board)
    return BoardRead.model_validate(board)


@router.get("/about", response_model=BoardAboutRead)
def get_about_board(
    session: SessionDep,
    user: User | None = Depends(get_optional_user),
    share_token: str | None = Query(default=None),
) -> Any:
    board = session.exec(select(Board).where(Board.type == BoardType.ABOUT)).first()
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="About board not found")
    _ensure_can_view_board(session, board, user, share_token)
    about = session.exec(select(BoardAbout).where(BoardAbout.board_id == board.id)).first()
    if about is None:
        about = BoardAbout(board_id=board.id, content=None)
        session.add(about)
        session.commit()
        session.refresh(about)
    return BoardAboutRead(board_id=board.id, content=about.content)


@router.patch("/about", response_model=BoardAboutRead)
def update_about_board(
    session: SessionDep, payload: BoardAboutUpdate, user: User = Depends(get_current_user)
) -> Any:
    board = session.exec(select(Board).where(Board.type == BoardType.ABOUT)).first()
    if board is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="About board not found")
    # only editable according to board rules
    if board.type != BoardType.ABOUT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not an About board")
    _ensure_can_edit_board(session, board, user)
    about = session.exec(select(BoardAbout).where(BoardAbout.board_id == board.id)).first()
    if about is None:
        about = BoardAbout(board_id=board.id, content=payload.content)
    else:
        about.content = payload.content
    session.add(about)
    session.commit()
    session.refresh(about)
    return BoardAboutRead(board_id=board.id, content=about.content)


@router.get("/{board_id}", response_model=BoardRead)
def get_board(
    session: SessionDep,
    board_id: int,
    user: User | None = Depends(get_optional_user),
    share_token: str | None = Query(default=None),
) -> Any:
    board = _get_board_or_404(session, board_id)
    _ensure_can_view_board(session, board, user, share_token)
    return BoardRead.model_validate(board)


@router.patch("/{board_id}", response_model=BoardRead)
def update_board(
    session: SessionDep,
    board_id: int,
    payload: BoardUpdate,
    user: User = Depends(get_current_user),
) -> Any:
    board = _get_board_or_404(session, board_id)
    if board.type != BoardType.COMMON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only common boards are editable"
        )
    if payload.name is not None:
        board.name = payload.name
    session.add(board)
    session.commit()
    session.refresh(board)
    return BoardRead.model_validate(board)


@router.delete("/{board_id}", status_code=status.HTTP_200_OK)
def delete_board(
    session: SessionDep, board_id: int, user: User = Depends(get_current_user)
) -> Response:
    board = _get_board_or_404(session, board_id)
    if board.type != BoardType.COMMON:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Only common boards can be deleted"
        )
    common_ids = session.exec(
        select(CardCommon.id).where(CardCommon.board_id == board.id)
    ).all()
    employee_ids = session.exec(
        select(CardEmployee.id).where(CardEmployee.board_id == board.id)
    ).all()
    service_ids = session.exec(
        select(CardService.id).where(CardService.board_id == board.id)
    ).all()

    if common_ids:
        session.exec(
            delete(TagToCard).where(TagToCard.card_id.in_(common_ids))
        )
        session.exec(delete(CardCommon).where(CardCommon.id.in_(common_ids)))
    if employee_ids:
        session.exec(delete(CardEmployee).where(CardEmployee.id.in_(employee_ids)))
    if service_ids:
        session.exec(delete(CardService).where(CardService.id.in_(service_ids)))

    session.exec(delete(ShareLink).where(ShareLink.board_id == board.id))
    session.exec(delete(BoardAbout).where(BoardAbout.board_id == board.id))
    session.delete(board)
    session.commit()
    return Response(status_code=status.HTTP_200_OK)





