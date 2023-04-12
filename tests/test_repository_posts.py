from datetime import datetime
from fastapi import Request, UploadFile
from unittest.mock import MagicMock, patch

import asyncio
import pytest
import io
from PIL import Image

from src.database.models import User, Post, Hashtag
import src.repository.posts as repository_posts
from src.schemas import PostUpdate


@pytest.fixture()
def current_user(user, session):
    current_user = session.query(User).filter(User.email == user.get('email')).first()
    if current_user is None:
        current_user = User(
            email=user.get('email'),
            username=user.get('username'),
            password=user.get('password')
        )  
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    return current_user


@pytest.fixture()
def post(current_user, session):
    post = session.query(Post).first()
    if post is None:
        post = Post(
            image_url="https://res.cloudinary.com/dybgf2pue/image/upload/c_fill,h_250,w_250/Dominic",
            title="cat",
            descr="pet",
            created_at=datetime.now(),
            user_id=current_user.id,
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
        "title": "other_post",
        "descr": "other_post",
        "hashtags": ["other_post"]
        }


@pytest.mark.asyncio
async def test_create_post(request: Request, session, current_user):
    file_data = io.BytesIO()
    image = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
    image.save(file_data, 'jpeg')
    file_data.seek(0)
    
    file = UploadFile(file_data)
    title = "test_post"
    descr = "test_post"
    hashtags = ["test_post"]
    response = await repository_posts.create_post(request, title, descr, hashtags, file, session, current_user)
    assert isinstance(response.image_url, str)
    assert response.title == title
    assert response.descr == descr


@pytest.mark.asyncio
async def test_get_all_posts(session):
    skip = 0
    limit = 100
    response = await repository_posts.get_all_posts(skip, limit, session)
    assert isinstance(response, list)
    assert len(response) >= 1


@pytest.mark.asyncio
async def test_get_my_posts(current_user, session):
    skip = 0
    limit = 100
    response = await repository_posts.get_my_posts(skip, limit, current_user, session)
    assert isinstance(response, list)
    assert len(response) >= 1


@pytest.mark.asyncio
async def test_get_post_by_id(post, current_user, session):
    response = await repository_posts.get_post_by_id(post.id, current_user, session)
    assert response.title == "test_post"
    assert response.descr == "test_post"


@pytest.mark.asyncio
async def test_get_posts_by_title(current_user, session):
    post_title = "test_post"
    response = await repository_posts.get_posts_by_title(post_title, current_user, session)
    assert isinstance(response, list)
    assert response[0].title == "test_post"
    assert response[0].descr == "test_post"


@pytest.mark.asyncio
async def test_get_posts_by_user_id(current_user, session):
    response = await repository_posts.get_posts_by_user_id(current_user.id, session)
    assert isinstance(response, list)
    assert response[0].title == "test_post"
    assert response[0].descr == "test_post"


@pytest.mark.asyncio
async def test_get_posts_by_username(current_user, session):
    response = await repository_posts.get_posts_by_username(current_user.username, session)
    assert isinstance(response, list)
    assert response[0].title == "test_post"
    assert response[0].descr == "test_post"


@pytest.mark.asyncio
async def test_get_posts_with_hashtag(session):
    hashtag_name = "test_post"
    response = await repository_posts.get_posts_with_hashtag(hashtag_name, session)
    assert isinstance(response, list)
    assert response[0].title == "test_post"
    assert response[0].descr == "test_post"


@pytest.mark.asyncio
async def test_get_post_comments(post, session):
    response = await repository_posts.get_post_comments(post.id, session)
    assert isinstance(response, list)


def test_get_hashtags(current_user, session):
    hashtag_titles = ["new_test_post"]
    response = repository_posts.get_hashtags(hashtag_titles, current_user, session)
    assert response[0].title == "new_test_post"


@pytest.mark.asyncio
async def test_searcher(post, session):
    keyword = post.title
    response = await repository_posts.searcher(keyword, session)
    assert isinstance(response, list)
    assert response[0].title == "test_post"
    assert response[0].descr == "test_post"
    assert response[0].id == post.id


@pytest.mark.asyncio
async def test_update_post(post, body, current_user, session):
    body = PostUpdate(**body)
    response = await repository_posts.update_post(post.id, body, current_user, session)
    assert response.title == "other_post"
    assert response.descr == "other_post"


@pytest.mark.asyncio
async def test_remove_post(post, current_user, session):
    await repository_posts.remove_post(post.id, current_user, session)
    response = await repository_posts.get_post_by_id(post.id, current_user, session)
    assert response == None
