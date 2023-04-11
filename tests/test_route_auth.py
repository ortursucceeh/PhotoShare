import sys
import os
from unittest.mock import MagicMock

from src.database.models import User
from src.conf.messages import ALREADY_EXISTS, EMAIL_NOT_CONFIRMED, INVALID_PASSWORD, INVALID_EMAIL, USER_NOT_ACTIVE

sys.path.append(os.getcwd())


def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.confirmed_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]


def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == ALREADY_EXISTS


def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == EMAIL_NOT_CONFIRMED
    

def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_verify = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    
    
def test_login_user_not_active(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_active = False
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    USER_NOT_ACTIVE
    assert response.status_code == 403, response.text
    data = response.json()
    assert data["detail"] == USER_NOT_ACTIVE


def test_login_wrong_password(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_active = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_PASSWORD


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == INVALID_EMAIL
