import requests
from fastapi import Request, UploadFile
from requests_toolbelt.multipart.encoder import MultipartEncoder

from datetime import datetime
from unittest.mock import MagicMock, patch
import io
from PIL import Image
import pytest
from src.database.models import User, Hashtag, Post
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


@pytest.fixture()
def post(user, token, session):
    cur_user = session.query(User).filter(User.email == user['email']).first()
    post = session.query(Post).first()
    if post is None:
        post = Post(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=cur_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


def test_create_post(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None 
        file_data = io.BytesIO()
        image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
        image.save(file_data, 'jpeg')
        file_data.seek(0)
        data = {
            "title": "test_post",
            "descr": "test_post",
            "hashtags": ["test_post"]
            }
        
        response = client.post(
            "/api/posts/new/",
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files={"file": ("test.jpg", file_data, "image/jpeg")}
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["title"] == "test_post"
        assert data["descr"] == "test_post"
        assert data["image_url"] != None
        assert "id" in data


def test_get_post(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_id/{post.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "test_post"
        assert "id" in data


def test_get_post_not_found(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_id/{post.id+1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_get_post_by_title(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            f"/api/posts/by_title/{post.title}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data[0]["title"] == "test_post"
        assert data[0]["descr"] == "test_post"
        assert data[0]["image_url"] != None


def test_get_post_by_title_not_found(client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.get(
            "/api/posts/by_title/other_test",
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
        assert len(data) >= 1


def test_update_post(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/posts/{post.id}",
            json={
                "title": "other_post",
                "descr": "other_post",
                "hashtags": ["other_post"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "other_post"
        assert data["descr"] == "other_post"
        assert "id" in data


def test_update_post_not_found(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/posts/{post.id+1}",
            json={
                "title": "other_post",
                "descr": "other_post",
                "hashtags": ["other_post"]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND


def test_delete_post(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/posts/{post.id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["title"] == "other_post"
        assert data["descr"] == "other_post"
        assert "id" in data


def test_repeat_delete_post(post, client, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/posts/{post.id-1}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, response.text
        data = response.json()
        assert data["detail"] == NOT_FOUND
        