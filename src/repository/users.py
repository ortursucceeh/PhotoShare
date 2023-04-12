from datetime import datetime
from typing import List

import cloudinary
import cloudinary.uploader
from sqlalchemy import  func
from sqlalchemy.orm import Session

from src.conf.config import init_cloudinary
from src.conf.messages import USER_NOT_ACTIVE
from src.database.models import User, UserRoleEnum, Comment, Rating, Post, BlacklistToken
from src.schemas import UserModel, UserProfileModel


async def get_me(user: User, db: Session) -> User:
    """
    The get_me function returns the user object of the current logged in user.
    
    
    :param user: User: Get the user id
    :param db: Session: Access the database
    :return: A user object
    """
    user = db.query(User).filter(User.id == user.id).first()
    return user


async def edit_my_profile(file, new_username, user: User, db: Session) -> User:
    """
    The edit_my_profile function allows a user to edit their profile.
    
    :param file: Upload the image to cloudinary
    :param new_username: Change the username of the user
    :param user: User: Get the user object from the database
    :param db: Session: Access the database
    :return: A user object
    """
    me = db.query(User).filter(User.id == user.id).first()
    if new_username:
        me.username = new_username
        
    init_cloudinary()
    cloudinary.uploader.upload(file.file, public_id=f'Photoshare/{me.username}',
                               overwrite=True, invalidate=True)
    url = cloudinary.CloudinaryImage(f'Photoshare/{me.username}')\
                        .build_url(width=250, height=250, crop='fill')
    me.avatar = url
    db.commit()
    db.refresh(me)
    return me


async def get_users(skip: int, limit: int, db: Session) -> List[User]:
    """
    The get_users function returns a list of users from the database.
    
    :param skip: int: Skip the first n records in the database
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database session to the function
    :return: A list of users
    """
    return db.query(User).offset(skip).limit(limit).all()


async def get_users_with_username(username: str, db: Session) -> List[User]:
    """
    The get_users_with_username function returns a list of users with the given username.
        Args:
            username (str): The username to search for.
            db (Session): A database session object.
        Returns:
            List[User]: A list of User objects that match the given criteria.
    
    :param username: str: Specify the type of data that is expected to be passed into the function
    :param db: Session: Pass the database session to the function
    :return: A list of users
    """
    return db.query(User).filter(func.lower(User.username).like(f'%{username.lower()}%')).all()


async def get_user_profile(username: str, db: Session) -> User:
    """
    The get_user_profile function returns a UserProfileModel object containing the user's username, email,
    avatar, created_at date and time (in UTC), is_active status (True or False),
    post count, comment count and rates count.
    
    :param username: str: Get the user profile of a specific user
    :param db: Session: Access the database
    :return: A userprofilemodel object
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        post_count = db.query(Post).filter(Post.user_id == user.id).count()
        comment_count = db.query(Comment).filter(Comment.user_id == user.id).count()
        rates_count = db.query(Rating).filter(Rating.user_id == user.id).count()
        user_profile = UserProfileModel(
                username=user.username,
                email=user.email,
                avatar=user.avatar,
                created_at=user.created_at, 
                is_active=user.is_active,
                post_count=post_count,
                comment_count=comment_count,
                rates_count=rates_count
            )
        return user_profile
    return None


async def get_all_commented_posts(user: User, db: Session):
    """
    The get_all_commented_posts function returns all posts that a user has commented on.
    
    :param user: User: Get the user object from the database
    :param db: Session: Pass the database session to the function
    :return: All posts that have been commented on by a user
    """
    return db.query(Post).join(Comment).filter(Comment.user_id == user.id).all()


async def get_all_liked_posts(user: User, db: Session):
    """
    The get_all_liked_posts function returns all posts that a user has liked.
        Args:
            user (User): The User object to get the liked posts for.
            db (Session): A database session to use for querying the database.
        Returns:
            List[Post]: A list of Post objects that have been liked by the specified User.
    
    :param user: User: Get the user's id
    :param db: Session: Pass the database session to the function
    :return: A list of posts that the user liked
    """
    return db.query(Post).join(Rating).filter(Rating.user_id == user.id).all()


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
    if len(db.query(User).all()) == 0: #  First user always admin
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


async def ban_user(email: str, db: Session) -> None:

    """
    The ban_user function takes in an email and a database session.
    It then finds the user with that email, sets their is_active field to False,
    and commits the change to the database.

    :param email: str: Identify the user to be banned
    :param db: Session: Pass in the database session
    :return: None, because we don't need to return anything
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
    """
    user = await get_user_by_email(email, db)
    user.role = role
    db.commit()


#### BLACKLIST #####

async def add_to_blacklist(token: str, db: Session) -> None:
    """
    The add_to_blacklist function adds a token to the blacklist.
        Args:
            token (str): The JWT that is being blacklisted.
            db (Session): The database session object used for querying and updating the database.
    
    :param token: str: Pass the token to be blacklisted
    :param db: Session: Create a new session with the database
    :return: None
    """
    blacklist_token = BlacklistToken(token=token, blacklisted_on=datetime.now())
    db.add(blacklist_token)
    db.commit()
    db.refresh(blacklist_token)
    
    
async def find_blacklisted_token(token: str, db: Session) -> None:
    """
    The find_blacklisted_token function takes a token and database session as arguments.
    It then queries the BlacklistToken table for any tokens that match the one passed in.
    If it finds a matching token, it returns that object.
    
    :param token: str: Pass the token to be checked
    :param db: Session: Connect to the database
    :return: A blacklisttoken object or none
    """
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    return blacklist_token
    
    
async def remove_from_blacklist(token: str, db: Session) -> None:
    """
    The remove_from_blacklist function removes a token from the blacklist.
        Args:
            token (str): The JWT to remove from the blacklist.
            db (Session): A database session object.
    
    :param token: str: Specify the token to be removed from the blacklist
    :param db: Session: Access the database
    :return: None
    """
    blacklist_token = db.query(BlacklistToken).filter(BlacklistToken.token == token).first()
    db.delete(blacklist_token)
