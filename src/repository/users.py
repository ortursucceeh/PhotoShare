from sqlalchemy.orm import Session

from src.database.models import User, UserRoleEnum
from src.schemas import UserModel


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


# async def confirmed_email(email: str, db: Session) -> None:
#     """
#     The confirmed_email function sets the confirmed field of a user to True.

#     :param email: str: Get the email of the user that is trying to confirm their account
#     :param db: Session: Pass the database session to the function
#     :return: None
#     """
#     user = await get_user_by_email(email, db)
#     user.is_verify = True
#     db.commit()


async def update_avatar(email, url: str, db: Session) -> User:
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
