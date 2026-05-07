from app.core.security import get_password_hash
from app.models import User, UserRole


def test_login_refresh_logout(client, session):
	user = User(
		username="employee",
		role=UserRole.EMPLOYEE,
		password_hash=get_password_hash("secret"),
	)
	session.add(user)
	session.commit()

	response = client.post(
		"/api/v1/auth/login",
		data={"username": "employee", "password": "secret"},
	)
	assert response.status_code == 200
	data = response.json()
	assert "access_token" in data
	assert response.cookies.get("refresh_token")

	response = client.post("/api/v1/auth/refresh")
	assert response.status_code == 200
	assert "access_token" in response.json()

	response = client.post("/api/v1/auth/logout")
	assert response.status_code == 200
