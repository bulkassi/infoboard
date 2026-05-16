from app.core.security import get_password_hash
from app.models import BoardType, User, UserRole


def test_card_tag_assignment_endpoints(client, session):
	user = User(username="tagger", role=UserRole.EMPLOYEE, password_hash=get_password_hash("pw"))
	session.add(user)
	session.commit()

	r = client.post("/api/v1/auth/login", data={"username": "tagger", "password": "pw"})
	assert r.status_code == 200
	token = r.json()["access_token"]
	headers = {"Authorization": f"Bearer {token}"}

	r = client.post("/api/v1/boards", json={"name": "Board"}, headers=headers)
	assert r.status_code == 201
	board_id = r.json()["id"]

	r = client.post("/api/v1/tags", json={"text": "Important"}, headers=headers)
	assert r.status_code == 201
	tag_id = r.json()["id"]

	r = client.post(
		f"/api/v1/boards/{board_id}/cards",
		json={"type": "common", "title": "Card"},
		headers=headers,
	)
	assert r.status_code == 201
	card_id = r.json()["id"]

	r = client.get(f"/api/v1/cards/{card_id}/tags", headers=headers)
	assert r.status_code == 200
	assert r.json() == []

	r = client.post(f"/api/v1/cards/{card_id}/tags/{tag_id}", headers=headers)
	assert r.status_code == 200
	assert len(r.json()) == 1
	assert r.json()[0]["id"] == tag_id

	r = client.get(f"/api/v1/cards/{card_id}/tags", headers=headers)
	assert r.status_code == 200
	assert [tag["id"] for tag in r.json()] == [tag_id]

	r = client.delete(f"/api/v1/cards/{card_id}/tags/{tag_id}", headers=headers)
	assert r.status_code == 200
	assert r.json() == []
