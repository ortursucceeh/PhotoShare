from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, Post, Hashtag
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


@pytest.fixture()
def tag(user, token, session):
    cur_user = session.query(User).filter(User.email == user['email']).first()
    tag = session.query(Hashtag).first()
    if tag is None:
        tag = Hashtag(
            title="dog",
            user_id=cur_user.id
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
    return tag


@pytest.fixture()
def body():
    return {
        "title": "string"
    }



def test_create_tag(body, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.post(f'/api/hashtags/new/', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get('title') is not None


def test_read_my_tags(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/my/',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "string"
        assert "id" in data[0]


def test_read_all_tags(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/all/',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)
        assert data[0]["title"] == "string"
        assert "id" in data[0]


def test_read_tag_by_id(tag, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/by_id/{tag.id}',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "string"
        assert "id" in data


def test_read_tag_by_id_not_found(tag, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(f'/api/hashtags/by_id/{tag.id+1}',
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Tag not found"


def test_update_tag(tag, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(f'/api/hashtags/upd_tag/{tag.id}',
                            json={"title": "new_test_tag"},
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "new_test_tag"
        assert "id" in data


def test_update_tag_not_found(tag, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(f'/api/hashtags/upd_tag/{tag.id+1}',
                            json={"title": "new_test_tag"},
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Tag not found"


def test_delete(tag, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(f"/api/hashtags/del/{tag.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "new_test_tag"
        assert "id" in data


def test_repeat_delete_tag(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(f"/api/hashtags/del/{1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == "Tag not found"

