from datetime import datetime
from unittest.mock import MagicMock, patch

import asyncio
import pytest

from src.database.models import User, Post
from src.repository.transform_post import transform_metod, show_qr
from src.tramsform_schemas import TransformBodyModel


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
    "art_audrey": True,
    "art_zorro": False,
    "cartoonify": False,
    "blur": False
  },
  "resize": {
    "use_filter": True,
    "crop": False,
    "fill": True,
    "height": 400,
    "width": 400
  },
  "text": {
    "use_filter": True,
    "font_size": 70,
    "text": "oooohhh"
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
    part_url = "image/upload/c_thumb,g_face,h_400,w_400/r_max/e_art:audrey/c_fill,g_auto,h_400,w_400/co_rgb:FFFF00,l_text:Times_70_bold:oooohhh/fl_layer_apply,g_south,y_20/c_scale,w_400/a_vflip/a_45/Dominic"
    response = await transform_metod(post.id, body, new_user, session)
    assert part_url in response.transform_url 


@pytest.mark.asyncio
async def test_show_qr(post, new_user, session):
    response = await show_qr(post.id, new_user, session)
    assert isinstance(response, str)
