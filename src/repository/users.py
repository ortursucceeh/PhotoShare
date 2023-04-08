from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.conf.messages import USER_NOT_ACTIVE
from src.database.models import User, UserRoleEnum, BlacklistToken
from src.schemas import UserModel


async def get_users(skip: int, limit: int, db: Session) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# get_user_by_username
# @router.get("/by_username/{user_name}", response_model=List[PostResponse])
# async def read_posts_by_username(user_name: str, db: Session = Depends(get_db),
#             current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_posts_by_username(user_name, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts

# async def get_all_commented_posts(user: User, db: Session):
#     return db.query(Post).join(Comment).filter(Comment.user_id == user.id).all()

# async def get_all_liked_posts(user: User, db: Session):
#     return db.query(Post).join(Rating).filter(Rating.user_id == user.id).all()

async def get_user_by_email(email: str, db: Session) -> User:
    """
    The get_user_by_email function takes in an email and a database session, then returns the user with that email.

    :param email: str: Get the email from the user
    :param db: Session: Pass a database session to the function
    :return: A user object if the email is found in the database
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    The create_user function creates a new user in the database.


    :param body: UserModel: Define the data that will be passed to the function
    :param db: Session: Pass in the database session
    :return: A user object
    """
    new_user = User(**body.dict())
    if len(db.query(User).all()) == 0: # First user always admin
        new_user.role = UserRoleEnum.admin
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    

    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Identify the user that is being updated
    :param token: str | None: Store the token in the database
    :param db: Session: Create a database session
    :return: None, but the return type is specified as str | none
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    The confirmed_email function sets the confirmed field of a user to True.

    :param email: str: Get the email of the user that is trying to confirm their account
    :param db: Session: Pass the database session to the function
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.is_verify = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> User:
    """
    The update_avatar function updates the avatar of a user.

    Args:
    email (str): The email address of the user to update.
    url (str): The URL for the new avatar image.
    db (Session, optional): A database session object to use instead of creating one locally. Defaults to None.  # noQA: E501 line too long, but this is an example!  # noQA: E501 line too long, but this is an example!  # noQA: E501 line too long, but this is an example!  # noQ

    :param email: Find the user in the database
    :param url: str: Specify the type of data that is being passed into the function
    :param db: Session: Pass the database session to the function
    :return: The user object with the updated avatar url
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def ban_user(email: str, db: Session) -> None:

    """
    The ban_user function takes in an email and a database session.
    It then finds the user with that email, sets their is_active field to False,
    and commits the change to the database.

    :param email: str: Identify the user to be banned
    :param db: Session: Pass in the database session
    :return: None, because we don't need to return anything
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.is_active = False
    db.commit()


async def make_user_role(email: str, role: UserRoleEnum, db: Session) -> None:

    """
    The make_user_role function takes in an email and a role, and then updates the user's role to that new one.
    Args:
    email (str): The user's email address.
    role (UserRoleEnum): The new UserRoleEnum for the user.

    :param email: str: Get the user by email
    :param role: UserRoleEnum: Set the role of the user
    :param db: Session: Pass the database session to the function
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.role = role
    db.commit()


async def add_to_blacklist(token: str, db: Session) -> None:
    blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.now())
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)
