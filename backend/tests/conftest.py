import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from app.core.db import get_session
from app.main import app


@pytest.fixture()
def session() -> Session:
	engine = create_engine(
		"sqlite:///:memory:",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
	)
	SQLModel.metadata.create_all(engine)
	with Session(engine) as session:
		yield session


@pytest.fixture()
def client(session: Session) -> TestClient:
	def _get_session_override():
		yield session

	app.dependency_overrides[get_session] = _get_session_override
	with TestClient(app) as client:
		yield client
	app.dependency_overrides.clear()
