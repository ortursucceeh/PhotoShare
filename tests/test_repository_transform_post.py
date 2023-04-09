from datetime import datetime
from unittest.mock import MagicMock, patch

import asyncio
import pytest

from src.database.models import User, Post
from src.repository.transform_post import transform_metod, show_qr
from src.tramsform_schemas import TransformBodyModel


# @pytest.fixture()
# def token(client, user, session, monkeypatch):
#     mock_send_email = MagicMock()
#     monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
#     client.post("/api/auth/signup", json=user)
#     current_user: User = session.query(User).filter(User.email == user.get('email')).first()
#     current_user.is_verify = True
#     session.commit()
#     response = client.post(
#         "/api/auth/login",
#         data={"username": user.get('email'), "password": user.get('password')},
#     )
#     data = response.json()
#     return data["access_token"]


@pytest.fixture()
def new_user(user, session):
    new_user = session.query(User).filter(User.email == user.get('email')).first()
    if new_user is None:
        new_user = User(
            email=user.get('email'),
            username=user.get('username'),
            password=user.get('password')
        )  
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
    return new_user


@pytest.fixture()
def post(new_user, session):
    post = session.query(Post).first()
    if post is None:
        post = Post(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=new_user.id,
            public_id="Dominic",
            done=True
        )
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


@pytest.fixture()
def body():
    return{
    "circle": {
        "use_filter": True,
        "height": 400,
        "width": 400
    },
    "effect": {
        "use_filter": True,
        "art_audrey": False,
        "art_zorro": True,
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
        "use_filter": True,
        "font_size": 70,
        "text": "Good"
    },
    "rotate": {
        "use_filter": True,
        "width": 400,
        "degree": 45
    }
    }


@pytest.mark.asyncio
async def test_transform_metod(post, body, new_user, session):
    body = TransformBodyModel(**body)
    url = "https://res.cloudinary.com/dybgf2pue/image/upload/c_thumb,g_face,h_400,w_400/r_max/c_crop,g_auto,h_400,w_400/c_scale,w_400/a_vflip/a_45/Dominic"
    response = await transform_metod(post.id, body, new_user, session)
    assert response.transform_url == url


@pytest.mark.asyncio
async def test_show_qr(post, new_user, session):
    response = await show_qr(post.id, new_user, session)
    assert type(response) == str
