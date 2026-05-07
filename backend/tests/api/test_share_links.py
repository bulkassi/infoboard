from app.core.security import get_password_hash
from app.models import User, UserRole


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
