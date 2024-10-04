import pytest
from app.extensions import db
from app import create_app
from app.config import TestConfig


@pytest.fixture(scope="module")
def test_app():
    app = create_app(config_class=TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope="module")
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def register_user(test_client):
    def _register_user(username="john", password="password123"):
        return test_client.post(
            "/api/register", json={"username": username, "password": password}
        )

    return _register_user


@pytest.fixture
def get_jwt_token(test_client):
    def _get_jwt_token(username="john", password="password123"):
        # First, register the user
        test_client.post(
            "/api/register", json={"username": username, "password": password}
        )
        # Then, login to get the JWT token
        response = test_client.post(
            "/api/login", json={"username": username, "password": password}
        )
        return response.get_json()["access_token"]

    return _get_jwt_token
