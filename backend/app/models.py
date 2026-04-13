from enum import Enum

from sqlmodel import Field, SQLModel


class HealthCheck(SQLModel, table=False):
    status: str = Field(default="ok")


class BoardType(str, Enum):
    STANDART = "Standart"
    MAIN = "Main"
    ABOUT = "About"
    EMPLOYEES = "Employees"
    SERVICES = "Services"


class Board(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    type: BoardType


class BoardUpdate(SQLModel):
    name: str | None = None
    type: BoardType | None = None
