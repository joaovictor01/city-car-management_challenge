def test_register_user(test_client, register_user):
    response = register_user("john", "password123")
    assert response.status_code == 201


def test_register_existing_user(test_client, register_user):
    response = register_user("john", "password123")
    assert response.status_code == 409


def test_login_user(test_client, register_user):
    register_user("john", "password123")
    response = test_client.post(
        "/api/login", json={"username": "john", "password": "password123"}
    )
    assert response.status_code == 200
    assert "access_token" in response.get_json()


def test_login_invalid_user(test_client):
    response = test_client.post(
        "/api/login", json={"username": "invalid", "password": "invalid"}
    )
    assert response.status_code == 401
