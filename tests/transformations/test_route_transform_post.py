from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.database.models import User, Post
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
def post_id(user, token, session):
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
    return post.id


@pytest.fixture()
def body():
    return{
    "circle": {
        "use_filter": True,
        "height": 400,
        "width": 400
    },
    "effect": {
        "use_filter": False,
        "art_audrey": False,
        "art_zorro": False,
        "cartoonify": False,
        "blur": False
    },
    "resize": {
        "use_filter": True,
        "crop": True,
        "fill": False,
        "height": 400,
        "width": 400
    },
    "text": {
        "use_filter": False,
        "font_size": 70,
        "text": ""
    },
    "rotate": {
        "use_filter": True,
        "width": 400,
        "degree": 45
    }
    }



def test_transform_metod(client, post_id, body, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.patch(f'/api/transformations/{post_id}', json=body,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert data.get('transform_url') is not None


def test_show_qr(client, post_id, user, token):
    with patch.object(auth_service, 'redis_cache') as r_mock:
        r_mock.get.return_value = None
        response = client.post(f'/api/transformations/qr/{post_id}', json=user,
                            headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200, response.text
        data = response.json()
        assert isinstance(data, str)
    