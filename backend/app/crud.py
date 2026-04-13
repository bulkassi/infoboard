from sqlmodel import Session, select

from app.models import Board, BoardType, BoardUpdate

INITIAL_BOARDS: list[Board] = [
    Board(id=0, name="Main", type=BoardType.MAIN),
    Board(id=1, name="About", type=BoardType.ABOUT),
    Board(id=2, name="Employees", type=BoardType.EMPLOYEES),
    Board(id=3, name="Services", type=BoardType.SERVICES),
    Board(id=4, name="Доска 1", type=BoardType.STANDART),
    Board(id=5, name="Доска 2", type=BoardType.STANDART),
]


def seed_boards(session: Session) -> None:
    existing_ids = set(session.exec(select(Board.id)).all())
    missing = [board for board in INITIAL_BOARDS if board.id not in existing_ids]
    if not missing:
        return
    for board in missing:
        session.add(board)
    session.commit()


def get_board_by_id(session: Session, board_id: int) -> Board | None:
    return session.get(Board, board_id)


def update_board_by_id(session: Session, board_id: int, payload: BoardUpdate) -> Board | None:
    board = session.get(Board, board_id)
    if board is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(board, key, value)

    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def delete_board_by_id(session: Session, board_id: int) -> bool:
    board = session.get(Board, board_id)
    if board is None:
        return False
    session.delete(board)
    session.commit()
    return True
