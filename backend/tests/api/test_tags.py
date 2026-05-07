from app.core.security import get_password_hash
from app.models import User, UserRole


def test_tags_crud(client, session):
    user = User(username="tagger", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
    session.add(user)
    session.commit()

    r = client.post("/api/v1/auth/login", data={"username": "tagger", "password": "pw"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # create tag
    r = client.post("/api/v1/tags", json={"text": "urgent"}, headers=headers)
    assert r.status_code == 201
    tag = r.json()
    assert tag["text"] == "urgent"

    # list tags
    r = client.get("/api/v1/tags", headers=headers)
    assert r.status_code == 200
    assert any(t["text"] == "urgent" for t in r.json())

    # update tag
    r = client.patch(f"/api/v1/tags/{tag['id']}", json={"text": "very-urgent"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["text"] == "very-urgent"

    # delete
    r = client.delete(f"/api/v1/tags/{tag['id']}", headers=headers)
    assert r.status_code == 200
