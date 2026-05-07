from app.core.security import get_password_hash
from app.models import User, UserRole


def test_file_upload_download_delete(client, session):
    user = User(username="filer", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
    session.add(user)
    session.commit()

    r = client.post("/api/v1/auth/login", data={"username": "filer", "password": "pw"})
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    data = {"file": ("img.png", b"\x89PNG\r\n", "image/png")}
    r = client.post("/api/v1/files", files=data, headers=headers)
    assert r.status_code == 201
    file_id = r.json()["id"]

    # download
    r = client.get(f"/api/v1/files/{file_id}")
    assert r.status_code == 200
    assert r.headers.get("content-type") == "image/png"

    # delete
    r = client.delete(f"/api/v1/files/{file_id}", headers=headers)
    assert r.status_code == 200
