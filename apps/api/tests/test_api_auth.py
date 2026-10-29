def test_login_successful(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user_id"] == test_user.id
    assert data["role"] == "resource_manager"


def test_login_invalid_password(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_get_current_user_profile(client, auth_headers, test_user):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id


def test_unauthorized_access(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
