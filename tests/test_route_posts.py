from unittest.mock import MagicMock, patch
import io
from PIL import Image
import pytest
from src.database.models import User, Hashtag
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND


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


def test_create_post(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None 
        file_data = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file_data, 'jpeg')
        file_data.seek(0)
        response = client.post(
            "/api/posts/new/",
            json={
                "request": "test_post",
                "title": "test_post",
                "descr": "test_post",
                "hashtags": []
            },
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["request"] == "test_post"
        assert data["title"] == "test_post"
        assert data["descr"] == "test_post"
        assert "id" in data


def test_get_post(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/by_id/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "test_post"
        assert "id" in data


def test_get_post_not_found(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/by_id/2",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND

def test_get_post_by_title(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/by_title/test_post",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "test_post"
        assert "id" in data

def test_get_post_by_title_not_found(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/by_title/test",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_posts(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/all",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, list)


def test_update_post(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        file_data = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file_data, 'jpeg')
        file_data.seek(0)
        response = client.put(
            "/api/posts/1",
            json={
                "request": "test_post",
                "title": "test_post",
                "descr": "test_post",
                "hashtags": []
            },
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["request"] == "test_post"
        assert data["title"] == "test_post"
        assert data["descr"] == "test_post"
        assert "id" in data


def test_update_post_not_found(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        file_data = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file_data, 'jpeg')
        file_data.seek(0)
        response = client.put(
            "/api/posts/2",
            json={
                "request": "test_post",
                "title": "test_post",
                "descr": "test_post",
                "hashtags": []
            },
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_delete_post(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/posts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "new_test_post"
        assert "id" in data


def test_repeat_delete_post(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            "/api/posts/1",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND