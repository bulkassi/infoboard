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
	refresh_token = response.cookies.get("refresh_token")
	assert refresh_token

	response = client.post("/api/v1/auth/logout", cookies={"refresh_token": refresh_token})
	assert response.status_code == 200
