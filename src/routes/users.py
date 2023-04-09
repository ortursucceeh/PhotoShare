from typing import List

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session


from src.database.connect_db import get_db
from src.repository import users as repository_users
from src.repository import posts as repository_posts
from src.database.models import User, UserRoleEnum
from src.schemas import PostResponse, UserModel, UserResponse, RequestEmail, UserDb, RequestRole
from src.conf.config import settings, init_cloudinary
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
async def read_my_profile(current_user: User = Depends(auth_service.get_current_user)):
    return current_user

#edit_me
#get_user_by_name(count_of_posts)


@router.patch('/avatar', response_model=UserDb)
async def update_avatar_user(file: UploadFile = File(), current_user: User = Depends(auth_service.get_current_user),
                             db: Session = Depends(get_db)):
    init_cloudinary()
    cloudinary.uploader.upload(file.file, public_id=f'Photoshare/{current_user.username}', overwrite=True)
    url = cloudinary.CloudinaryImage(f'Photoshare/{current_user.username}')\
                        .build_url(width=250, height=250, crop='fill')
    user = await repository_users.update_avatar(current_user.email, url, db)
    return user
    
    
@router.get("/all", response_model=List[UserDb], dependencies=[Depends(allowed_get_all_users)])
async def read_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = await repository_users.get_users(skip, limit, db)
    return users


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
        return {"msg": USER_NOT_ACTIVE}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE)


@router.patch("/make_role/{email}/", dependencies=[Depends(allowed_change_user_role)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if body.role == user.role:
        return {"msg": USER_ROLE_EXISTS}
    else:
        await repository_users.make_user_role(body.email, body.role, db)
        return {"msg": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}


