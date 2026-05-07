from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel


class HealthCheck(SQLModel, table=False):
    status: str = Field(default="ok")


class UserRole(str, Enum):
    EMPLOYEE = "employee"
    ADMIN = "admin"


class BoardType(str, Enum):
    COMMON = "common"
    MAIN = "main"
    ABOUT = "about"
    EMPLOYEES = "employees"
    SERVICES = "services"


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    role: UserRole = Field(default=UserRole.EMPLOYEE)
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RefreshSession(SQLModel, table=True):
    token_hash: str = Field(index=True, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime
    revoked_at: Optional[datetime] = None


class Board(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    type: BoardType
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")


class BoardAbout(SQLModel, table=True):
    board_id: int = Field(foreign_key="board.id", primary_key=True)
    content: Optional[str] = None


class ShareLink(SQLModel, table=True):
    token: str = Field(primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime


class File(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str
    mime_type: str
    size: int
    content: bytes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    text_color: str = "#000000"
    background_color: str = "#FFFFFF"
    global_: bool = Field(default=False, alias="global")
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")


class CardBase(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    board_id: int = Field(foreign_key="board.id")
    file_id: Optional[int] = Field(default=None, foreign_key="file.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CardCommon(CardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, foreign_key="cardbase.id")
    title: Optional[str] = None
    content: Optional[str] = None
    col: Optional[int] = 1
    row: Optional[int] = 1
    col_span: Optional[int] = 1
    row_span: Optional[int] = 1


class TagToCard(SQLModel, table=True):
    card_id: int = Field(foreign_key="cardcommon.id", primary_key=True)
    tag_id: int = Field(foreign_key="tag.id", primary_key=True)


class CardEmployee(CardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, foreign_key="cardbase.id")
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    position: Optional[str] = None


class CardService(CardBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, foreign_key="cardbase.id")
    name: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None


class UserRead(SQLModel):
    id: int
    username: str
    role: UserRole


class UserCreate(SQLModel):
    username: str
    password: str
    role: UserRole = UserRole.EMPLOYEE


class UserUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None


class UserSelfUpdate(SQLModel):
    username: Optional[str] = None
    password: Optional[str] = None


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(SQLModel):
    username: str
    password: str


class BoardRead(SQLModel):
    id: int
    name: str
    type: BoardType
    owner_id: Optional[int]


class BoardCreate(SQLModel):
    name: str


class BoardUpdate(SQLModel):
    name: Optional[str] = None


class BoardAboutRead(SQLModel):
    board_id: int
    content: Optional[str]


class BoardAboutUpdate(SQLModel):
    content: Optional[str] = None


class ShareLinkRead(SQLModel):
    token: str
    board_id: int
    expires_at: datetime


class ShareLinkCreate(SQLModel):
    pass


class FileRead(SQLModel):
    id: int
    filename: str
    mime_type: str
    size: int


class TagRead(SQLModel):
    id: int
    text: str
    text_color: str
    background_color: str
    global_: bool = Field(alias="global")
    owner_id: Optional[int]


class TagCreate(SQLModel):
    text: str
    text_color: str = "#000000"
    background_color: str = "#FFFFFF"
    global_: bool = Field(default=False, alias="global")


class TagUpdate(SQLModel):
    text: Optional[str] = None
    text_color: Optional[str] = None
    background_color: Optional[str] = None
    global_: Optional[bool] = Field(default=None, alias="global")


class CardRead(SQLModel):
    id: int
    type: str
    board_id: int
    col: Optional[int] = None
    row: Optional[int] = None
    col_span: Optional[int] = None
    row_span: Optional[int] = None
    file_id: Optional[int]
    title: Optional[str] = None
    content: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    tag_ids: list[int] = Field(default_factory=list)


class CardCreate(SQLModel):
    type: str
    title: Optional[str] = None
    content: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    col: int = 1
    row: int = 1
    col_span: int = 1
    row_span: int = 1
    file_id: Optional[int] = None
    tag_ids: list[int] = Field(default_factory=list)


class CardUpdate(SQLModel):
    title: Optional[str] = None
    content: Optional[str] = None
    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    link: Optional[str] = None
    col: Optional[int] = None
    row: Optional[int] = None
    col_span: Optional[int] = None
    row_span: Optional[int] = None
    file_id: Optional[int] = None
    tag_ids: Optional[list[int]] = None


class CardPositionUpdate(SQLModel):
    col: int
    row: int
    col_span: int
    row_span: int
