import json
from unittest.mock import MagicMock
from datetime import datetime
import pytest

from src.database.models import User, Post

from src.services.auth import auth_service


@pytest.mark.parametrize("post_id, user_id, result", [
    (1, 1, 200),  # own post
    (2, 2, 200)  # another user
])
def test_create_post(session, post_id, user_id, result):
    test_post = Post()
    test_post.id = post_id
    test_post.image_url = "image_url"
    test_post.transform_url = "transform_url"
    test_post.title = "title"
    test_post.descr = "descr"
    test_post.created_at = datetime.now()
    test_post.updated_at = datetime.now()
    test_post.done = True
    test_post.user_id = user_id
    test_post.hashtags = []
    test_post.public_id = "888"
    test_post.avg_rating = None

    session.add(test_post)
    session.commit()


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


@pytest.mark.parametrize("post_id, rate, result", [
    (1, 5, 423),  # Response [423 Locked]
    (2, 3, 200),  # Response [200]
    (3, 3, 404)  # Response [404]
])
def test_create_rating(session, client, token, post_id, rate, result):
    response = client.post(
        f"api/ratings/posts/{post_id}/{rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("rate_id, new_rate, result", [
    (1, 5, 200),
    (2, 3, 404),
    (3, 3, 404)
])
def test_edit_rating(session, client, token, rate_id, new_rate, result):
    response = client.put(
        f"api/ratings/edit/{rate_id}/{new_rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("rate_id, result", [
    (1, 200),
    (2, 404),
    (3, 404)
])
def test_delete_rating(session, client, token, rate_id, result):
    response = client.delete(
        f"api/ratings/delete/{rate_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


@pytest.mark.parametrize("post_id, rate, result", [
    (1, 5, 423),  # Response [423 Locked]
    (2, 3, 200),  # Response [200]
    (3, 3, 404)  # Response [404]
])
def test_create_rating_2(session, client, token, post_id, rate, result):
    response = client.post(
        f"api/ratings/posts/{post_id}/{rate}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


def test_all_ratings(session, client, token):

    response = client.get(
        "api/ratings/all",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert type(response.json()) == list


def test_all_my_rates(session, client, token):
    response = client.get(
        "api/ratings/all_my",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert type(response.json()) == list


@pytest.mark.parametrize("user_id, post_id, result", [
    (1, 2, 200),
    (1, 3, 404)
])
def test_user_for_post(session, client, token, user_id, post_id, result):

    response = client.get(
        f"api/ratings/user_post/{user_id}/{post_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == result


def test_commented(session, client, token):
    response = client.get(
        "api/ratings/post/2",
        headers={"Authorization": f"Bearer {token}"}
    )
    print(response.json())

    assert response.status_code == 200
