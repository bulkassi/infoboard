from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from app import crud
from app.core.db import get_session
from app.models import Board, BoardUpdate

router = APIRouter(prefix="/boards", tags=["boards"])


@router.get("/{board_id}", response_model=Board)
def get_board(board_id: int, session: Session = Depends(get_session)) -> Board:
    board = crud.get_board_by_id(session, board_id)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.put("/{board_id}", response_model=Board)
def update_board(board_id: int, payload: BoardUpdate, session: Session = Depends(get_session)) -> Board:
    board = crud.update_board_by_id(session, board_id, payload)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


@router.delete("/{board_id}", status_code=204)
def delete_board(board_id: int, session: Session = Depends(get_session)) -> Response:
    deleted = crud.delete_board_by_id(session, board_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Board not found")
    return Response(status_code=204)
