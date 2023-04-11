from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, Comment, Post
from src.services.auth import auth_service


@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.is_verify = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]


@pytest.fixture(scope="module")
def fix_comment():
    comment = {
        "text": "Test text for new comment",
        "id": 1,
        "created_at": "2023-04-09T22:50:03.062Z",
        "updated_at": None,
        "user_id": 1,
        "post_id": 1,
        "update_status": False
    }
    return comment


def test_create_comment(client, token):
    response = client.post(
        "api/comments/new/1", json={"text": "Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200, response.text

    body_data = response.json()
    assert body_data == {
        "text": "Test text for new comment",
        "id": 1,
        "created_at": f"{body_data['created_at']}",
        "updated_at": None,
        "user_id": 1,
        "post_id": 1,
        "update_status": False
    }


def test_edit_comment(client, session, token, user):
    response = client.put(
        "api/comments/edit/1", json={"text": "NEW Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_delete_comment(client, session, token):
    response = client.put(
        "api/comments/edit/1", json={"text": "NEW Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_create_comment_2(client, token):
    response = client.post(
        "api/comments/new/1", json={"text": "Test text for new comment"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_get_single_comm(client, session, token):
    response = client.get("api/comments/single/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text


def test_comment_by_auth(client, session, token):
    response = client.get(
        "api/comments/by_author/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text


def test_comm_post_auth(client, session, token):
    response = client.get(
        "api/comments/post_by_author/1/1",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200, response.text
