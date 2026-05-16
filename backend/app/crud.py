from datetime import datetime

from sqlalchemy import text
from sqlmodel import Session, select

from .core.security import get_password_hash
from .models import Board, BoardAbout, BoardType, User, UserRole

INITIAL_BOARDS: list[Board] = [
    Board(id=1, name="Main", type=BoardType.MAIN),
    Board(id=2, name="About", type=BoardType.ABOUT),
    Board(id=3, name="Employees", type=BoardType.EMPLOYEES),
    Board(id=4, name="Services", type=BoardType.SERVICES),
]


def seed_boards(session: Session) -> None:
    existing_types = set(session.exec(select(Board.type)).all())
    missing = [board for board in INITIAL_BOARDS if board.type not in existing_types]
    if not missing:
        _sync_board_id_sequence(session)
        return
    for board in missing:
        session.add(board)
    session.commit()
    _sync_board_id_sequence(session)


def _sync_board_id_sequence(session: Session) -> None:
    bind = session.get_bind()
    if bind is None or bind.dialect.name != "postgresql":
        return

    session.exec(
        text(
            "SELECT setval(pg_get_serial_sequence('board', 'id'), "
            "COALESCE((SELECT MAX(id) FROM board), 1), true)"
        )
    )
    session.commit()


def seed_about_content(session: Session) -> None:
    about_board = session.exec(
        select(Board).where(Board.type == BoardType.ABOUT)
    ).first()
    if about_board is None:
        return
    existing = session.exec(
        select(BoardAbout).where(BoardAbout.board_id == about_board.id)
    ).first()
    if existing is not None:
        return
    session.add(BoardAbout(board_id=about_board.id, content=None))
    session.commit()


def seed_admin_user(session: Session, username: str, password: str) -> None:
    existing = session.exec(select(User).where(User.username == username)).first()
    if existing is not None:
        return
    session.add(
        User(
            username=username,
            role=UserRole.ADMIN,
            password_hash=get_password_hash(password),
            created_at=datetime.utcnow(),
        )
    )
    session.commit()
