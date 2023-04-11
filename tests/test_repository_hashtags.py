from datetime import datetime
from unittest.mock import MagicMock, patch

import asyncio
import pytest

from src.database.models import User, Hashtag
import src.repository.hashtags as repository_tag
from src.schemas import HashtagBase


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
def tag(user, session):
    cur_user = session.query(User).filter(User.email == user['email']).first()
    tag = session.query(Hashtag).first()
    if tag is None:
        tag = Hashtag(
            title="dog",
            created_at=datetime.now(),
            user_id=cur_user.id
        )
        session.add(tag)
        session.commit()
        session.refresh(tag)
    return tag


@pytest.fixture()
def body():
    return{
  "title": "string"
    }


@pytest.fixture()
def new_body():
    return{
  "title": "dog"
    }


@pytest.mark.asyncio
async def test_create_tag(body, new_user, session):
    body = HashtagBase(**body)
    response = await repository_tag.create_tag(body, new_user, session)
    assert response.title == "string"


@pytest.mark.asyncio
async def test_get_my_tags(new_user, session):
    skip = 0
    limit = 100
    response = await repository_tag.get_my_tags(skip, limit, new_user, session)
    assert isinstance(response, list)
    assert len(response) >= 1


@pytest.mark.asyncio
async def test_get_all_tags(session):
    skip = 0
    limit = 100
    response = await repository_tag.get_all_tags(skip, limit, session)
    assert isinstance(response, list)
    assert len(response) >= 1


@pytest.mark.asyncio
async def test_get_tag_by_id(tag, session):
    response = await repository_tag.get_tag_by_id(tag.id, session)
    assert response.title == "string"


@pytest.mark.asyncio
async def test_update_tag(tag, new_body, session):
    body = HashtagBase(**new_body)
    response = await repository_tag.update_tag(tag.id, body, session)
    assert response.title == "dog"


@pytest.mark.asyncio
async def test_remove_tag(tag, session):
    await repository_tag.remove_tag(tag.id, session)
    skip = 0
    limit = 100
    response = await repository_tag.get_all_tags(skip, limit, session)
    assert len(response) == 0