import pytest

from src.database.models import User
from src.repository import users as repository_users
from src.schemas import UserModel
from src.database.models import UserRoleEnum

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
def second_user(session):
    new_user = User(
        username='second_user',
        email='second_user@example.com',
        password='qweqwe123123',
    )  
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@pytest.mark.asyncio
async def test_get_me(new_user, session):
    response = await repository_users.get_me(new_user, session)
    assert response.username == "artur4ik"
    assert response.email == "artur4ik@example.com"


@pytest.mark.asyncio
async def test_get_users(new_user, second_user, session):
    response = await repository_users.get_users(0, 100, session)
    assert isinstance(response, list)
    assert len(response) == 2


@pytest.mark.asyncio
async def test_get_users_with_username(new_user, session):
    response = await repository_users.get_users_with_username("artur", session)
    assert isinstance(response, list)
    assert response[0].username == "artur4ik"
    assert response[0].email == "artur4ik@example.com"
    
    
@pytest.mark.asyncio
async def test_get_user_profile(new_user, session):
    response = await repository_users.get_user_profile("artur4ik", session)
    assert response.username == "artur4ik"
    assert response.email == "artur4ik@example.com"
    assert response.post_count == 0
    assert response.comment_count == 0
    assert response.rates_count == 0
    
    
@pytest.mark.asyncio
async def test_get_all_commented_posts(new_user, session):
    response = await repository_users.get_all_commented_posts(new_user, session)
    assert isinstance(response, list)
    assert len(response) == 0


@pytest.mark.asyncio
async def test_get_all_liked_posts(new_user, session):
    response = await repository_users.get_all_liked_posts(new_user, session)
    assert isinstance(response, list)
    assert len(response) == 0
    
    
@pytest.mark.asyncio
async def test_get_user_by_email(new_user, session):
    response = await repository_users.get_user_by_email("second_user@example.com", session)
    assert response.username == "second_user"
    assert response.email == "second_user@example.com"
    
@pytest.mark.asyncio
async def test_create_user(user, session):
    test_user = UserModel(
        username="test_user",
        email="test_user@example.com",
        password="123456789",
        avatar="url-avatar"
    )
    response = await repository_users.create_user(test_user, session)
    assert response.username == "test_user"
    assert response.email == "test_user@example.com"
    
    
@pytest.mark.asyncio
async def test_confirmed_email(user, session):
    response = await repository_users.confirmed_email("second_user@example.com", session)
    second_user = await repository_users.get_user_by_email("second_user@example.com", session)
    assert second_user.is_verify == True


@pytest.mark.asyncio
async def test_ban_user(user, session):
    response = await repository_users.ban_user("second_user@example.com", session)
    second_user = await repository_users.get_user_by_email("second_user@example.com", session)
    assert second_user.is_active == False
    
    
@pytest.mark.asyncio
async def test_make_user_role(user, session):
    response = await repository_users.make_user_role("second_user@example.com", "moder", session)
    second_user = await repository_users.get_user_by_email("second_user@example.com", session)
    assert second_user.role == UserRoleEnum.moder



    