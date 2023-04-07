from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session


from src.database.connect_db import get_db
from src.repository import users as repository_users
from src.database.models import User, UserRoleEnum
from src.schemas import UserModel, UserResponse, RequestEmail, UserDb, RequestRole
from src.conf.config import settings, init_cloudinary
from src.services.auth import auth_service
from src.services.roles import RoleChecker
from src.conf.messages import USER_ROLE_EXIST, INVALID_EMAIL, USER_NOT_ACTIVE, USER_ALREADY_NOT_ACTIVE,\
    USER_CHANGE_ROLE_TO

router = APIRouter(prefix='/users', tags=["users"])

allowed_get_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_remove_user = RoleChecker([UserRoleEnum.admin])

@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    
    init_cloudinary()
    cloudinary.uploader.upload(file.file, public_id=f'Photoshare/{current_user.username}', overwrite=True)
    url = cloudinary.CloudinaryImage(f'Photoshare/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill')
    user = await repository_users.update_avatar(current_user.email, url, db)
    return user
    
    
@router.get("/all", response_model=List[UserDb], dependencies=[Depends(allowed_get_user)])
async def read_all_user(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_all_user function returns a list of users.

    :param skip: int: Skip the first n number of users in the database
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A list of users
    """
    users = await repository_users.get_users(skip, limit, db)
    return users


# ban_user_by_email
@router.put("/ban/{email}", dependencies=[Depends(allowed_remove_user)])
async def ban_user_by_email(body: RequestEmail, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    """
    The ban_user_by_email function is used to ban a user by email.

    :param body: RequestEmail: Receive the email of the user to be banned
    :param db: Session: Connect to the database
    :param current_user: User: Get the current user
    :return: A dictionary with a message
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if user.is_active:
        await repository_users.ban_user(user.email, db)
        return {"msg": USER_NOT_ACTIVE}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE)


# make admin
@router.put("/make_role/{email}", dependencies=[Depends(allowed_remove_user)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    """
    The make_role_by_email function is used to change the role of a user.
        The function takes in an email and a role, and then changes the user's role to that specified.
        If no such user exists, it returns an error message saying so.

    :param body: RequestRole: Get the email and role from the request body
    :param db: Session: Get the database session
    :param current_user: User: Get the current user that is logged in
    :return: A message that the user's role has been changed
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if body.role == user.role:
        return {"msg": USER_ROLE_EXIST}
    else:
        await repository_users.make_user_role(body.email, body.role, db)
        return {"msg": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}

# get all users

# get_user_by_name

# get_userProfile_by_name

# make_moder

# make_user

# ban_user_by_email



