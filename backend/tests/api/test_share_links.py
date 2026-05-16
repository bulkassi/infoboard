from app.core.security import get_password_hash
from app.models import User, UserRole, Board, BoardType, ShareLink
from datetime import datetime, timezone, timedelta


def test_share_links_create_resolve_delete(client, session):
    user = User(username="sharer", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
    session.add(user)
    session.commit()

    r = client.post("/api/v1/auth/login", data={"username": "sharer", "password": "pw"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create board
    r = client.post("/api/v1/boards", json={"name": "SBoard"}, headers=headers)
    assert r.status_code == 201
    board_id = r.json()["id"]

    r = client.post(f"/api/v1/boards/{board_id}/share-links", json={}, headers=headers)
    assert r.status_code == 200
    token_val = r.json()["token"]

    r = client.get(f"/api/v1/share-links/{token_val}/board")
    assert r.status_code == 200

    r = client.delete(f"/api/v1/share-links/{token_val}", headers=headers)
    assert r.status_code == 200


def test_list_share_links(client, session):
	user = User(username="linker", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
	session.add(user)
	session.commit()

	r = client.post("/api/v1/auth/login", data={"username": "linker", "password": "pw"})
	token = r.json()["access_token"]
	headers = {"Authorization": f"Bearer {token}"}

	# Create board
	r = client.post("/api/v1/boards", json={"name": "LinkBoard"}, headers=headers)
	board_id = r.json()["id"]

	# Create multiple share links
	r = client.post(f"/api/v1/boards/{board_id}/share-links", json={}, headers=headers)
	assert r.status_code == 200
	token1 = r.json()["token"]

	r = client.post(f"/api/v1/boards/{board_id}/share-links", json={}, headers=headers)
	assert r.status_code == 200
	token2 = r.json()["token"]

	# List all share links
	r = client.get(f"/api/v1/boards/{board_id}/share-links", headers=headers)
	assert r.status_code == 200
	tokens = [link["token"] for link in r.json()]
	assert token1 in tokens
	assert token2 in tokens
	assert len(tokens) == 2


def test_share_link_expired(client, session):
	user = User(username="exp_tester", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
	session.add(user)
	session.commit()

	# Create board and share link with past expiry
	board = Board(name="ExpBoard", type=BoardType.COMMON, owner_id=1)
	session.add(board)
	session.commit()
	
	past_time = datetime.now(timezone.utc) - timedelta(hours=1)
	share = ShareLink(token="expired_token_123", board_id=board.id, expires_at=past_time)
	session.add(share)
	session.commit()

	# Try to resolve expired link
	r = client.get("/api/v1/share-links/expired_token_123/board")
	assert r.status_code == 410  # HTTP 410 Gone
	assert "expired" in r.json()["detail"].lower()
