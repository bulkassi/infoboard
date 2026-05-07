from app.core.security import get_password_hash
from app.models import User, UserRole, BoardType


def test_cards_crud_and_position(client, session):
    user = User(username="carder", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
    session.add(user)
    session.commit()

    # login
    r = client.post("/api/v1/auth/login", data={"username": "carder", "password": "pw"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create a COMMON board
    r = client.post("/api/v1/boards", json={"name": "MyBoard"}, headers=headers)
    assert r.status_code == 201
    board_id = r.json()["id"]

    # create a common card
    payload = {"type": "common", "title": "T1", "content": "C1"}
    r = client.post(f"/api/v1/boards/{board_id}/cards", json=payload, headers=headers)
    assert r.status_code == 201
    card_id = r.json()["id"]

    # update card
    r = client.patch(f"/api/v1/cards/{card_id}", json={"title": "T2"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["title"] == "T2"

    # update position
    r = client.patch(f"/api/v1/cards/{card_id}/position", json={"col":2,"row":3,"col_span":1,"row_span":1}, headers=headers)
    assert r.status_code == 200
    assert r.json()["col"] == 2

    # delete
    r = client.delete(f"/api/v1/cards/{card_id}", headers=headers)
    assert r.status_code == 200
