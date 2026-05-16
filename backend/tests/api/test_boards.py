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


def test_board_crud_and_about(client, session):
	user = User(
		username="board_admin",
		role=UserRole.ADMIN,
		password_hash=get_password_hash("pw"),
	)
	session.add(user)
	session.commit()

	r = client.post(
		"/api/v1/auth/login",
		data={"username": "board_admin", "password": "pw"}
	)
	token = r.json()["access_token"]
	headers = {"Authorization": f"Bearer {token}"}

	# Create board
	r = client.post(
		"/api/v1/boards",
		json={"name": "Test Board"},
		headers=headers
	)
	assert r.status_code == 201
	board_id = r.json()["id"]
	assert r.json()["name"] == "Test Board"

	# Get single board
	r = client.get(f"/api/v1/boards/{board_id}", headers=headers)
	assert r.status_code == 200
	assert r.json()["name"] == "Test Board"

	# Update board
	r = client.patch(
		f"/api/v1/boards/{board_id}",
		json={"name": "Updated Board"},
		headers=headers
	)
	assert r.status_code == 200
	assert r.json()["name"] == "Updated Board"

	# Delete board
	r = client.delete(f"/api/v1/boards/{board_id}", headers=headers)
	assert r.status_code == 200
