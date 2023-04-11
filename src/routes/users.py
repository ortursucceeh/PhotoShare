from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database.connect_db import get_db
from src.repository import users as repository_users
from src.database.models import User, UserRoleEnum
from src.schemas import PostResponse, UserProfileModel, UserResponseModel, RequestEmail, UserDb, RequestRole
from src.services.auth import auth_service
from src.services.roles import RoleChecker
from src.conf.messages import NOT_FOUND, USER_ROLE_EXISTS, INVALID_EMAIL, USER_NOT_ACTIVE, USER_ALREADY_NOT_ACTIVE,\
    USER_CHANGE_ROLE_TO

router = APIRouter(prefix='/users', tags=["users"])

allowed_get_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_get_all_users = RoleChecker([UserRoleEnum.admin])
allowed_remove_user = RoleChecker([UserRoleEnum.admin])
allowed_ban_user = RoleChecker([UserRoleEnum.admin])
allowed_change_user_role = RoleChecker([UserRoleEnum.admin])


@router.get("/me/", response_model=UserDb)
async def read_my_profile(current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    user = await repository_users.get_me(current_user, db)
    return user


@router.put("/edit_me/", response_model=UserDb)
async def edit_my_profile(avatar: UploadFile = File(), new_username: str = Form(None),
                          current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    updated_user = await repository_users.edit_my_profile(avatar, new_username, current_user, db)
    return updated_user

    
@router.get("/all", response_model=List[UserDb], dependencies=[Depends(allowed_get_all_users)])
async def read_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = await repository_users.get_users(skip, limit, db)
    return users

@router.get("/users_with_username/{username}", response_model=List[UserResponseModel],
            dependencies=[Depends(allowed_get_user)])
async def read_users_by_username(username: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    users = await repository_users.get_users_with_username(username, db)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return users

@router.get("/user_profile_with_username/{username}", response_model=UserProfileModel,
            dependencies=[Depends(allowed_get_user)])
async def read_user_profile_by_username(username: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    user_profile = await repository_users.get_user_profile(username, db)
    if user_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return user_profile


@router.get("/commented_posts_by_me/", response_model=List[PostResponse])
async def read_commented_posts_by_me(db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_users.get_all_commented_posts(current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/rated_posts_by_me/", response_model=List[PostResponse])
async def read_liked_posts_by_me(db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_users.get_all_liked_posts(current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.patch("/ban/{email}/", dependencies=[Depends(allowed_ban_user)])
async def ban_user_by_email(body: RequestEmail, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if user.is_active:
        await repository_users.ban_user(user.email, db)
        return {"message": USER_NOT_ACTIVE}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE)


@router.patch("/make_role/{email}/", dependencies=[Depends(allowed_change_user_role)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if body.role == user.role:
        return {"message": USER_ROLE_EXISTS}
    else:
        await repository_users.make_user_role(body.email, body.role, db)
        return {"message": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}


