from app.core.security import get_password_hash
from app.models import Board, BoardType, User, UserRole


def test_public_board_visibility(client, session):
	session.add(Board(name="Main", type=BoardType.MAIN))
	session.add(Board(name="About", type=BoardType.ABOUT))
	session.add(Board(name="User", type=BoardType.COMMON, owner_id=1))
	session.commit()

	response = client.get("/api/v1/boards")
	assert response.status_code == 200
	board_types = {item["type"] for item in response.json()}
	assert BoardType.COMMON.value not in board_types
	assert BoardType.MAIN.value in board_types
	assert BoardType.ABOUT.value in board_types


def test_authenticated_board_visibility(client, session):
	user = User(
		username="employee",
		role=UserRole.EMPLOYEE,
		password_hash=get_password_hash("secret"),
	)
	session.add(user)
	session.add(Board(name="Main", type=BoardType.MAIN))
	session.add(Board(name="User", type=BoardType.COMMON, owner_id=1))
	session.commit()

	response = client.post(
		"/api/v1/auth/login", data={"username": "employee", "password": "secret"}
	)
	access_token = response.json()["access_token"]

	response = client.get(
		"/api/v1/boards", headers={"Authorization": f"Bearer {access_token}"}
	)
	assert response.status_code == 200
	board_types = {item["type"] for item in response.json()}
	assert BoardType.COMMON.value in board_types
