from app.core.security import get_password_hash
from app.models import User, UserRole


def test_admin_user_crud(client, session):
    admin = User(username="admin", role=UserRole.ADMIN, password_hash=get_password_hash("adminpw"))
    session.add(admin)
    session.commit()

    # login as admin
    resp = client.post("/api/v1/auth/login", data={"username": "admin", "password": "adminpw"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create user
    r = client.post("/api/v1/users", json={"username": "u1", "password": "pw", "role": "employee"}, headers=headers)
    assert r.status_code == 201

    # list users includes created
    r = client.get("/api/v1/users", headers=headers)
    assert r.status_code == 200
    assert any(u["username"] == "u1" for u in r.json())

    # update user
    user_id = next(u["id"] for u in r.json() if u["username"] == "u1")
    r = client.patch(f"/api/v1/users/{user_id}", json={"username": "u1b"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "u1b"

    # delete user
    r = client.delete(f"/api/v1/users/{user_id}", headers=headers)
    assert r.status_code == 200


def test_user_self_profile(client, session):
    user = User(username="you", role=UserRole.EMPLOYEE, password_hash=get_password_hash("secret"))
    session.add(user)
    session.commit()

    r = client.post("/api/v1/auth/login", data={"username": "you", "password": "secret"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = client.get("/api/v1/users/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "you"

    r = client.patch("/api/v1/users/me", json={"username": "you2"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["username"] == "you2"
