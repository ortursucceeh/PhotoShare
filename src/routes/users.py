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
    users = await repository_users.get_users(skip, limit, db)
    return users


@router.put("/ban/{email}", dependencies=[Depends(allowed_remove_user)])
async def ban_user_by_email(body: RequestEmail, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if user.is_active:
        await repository_users.ban_user(user.email, db)
        return {"msg": USER_NOT_ACTIVE}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE)


@router.put("/make_role/{email}", dependencies=[Depends(allowed_remove_user)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if body.role == user.role:
        return {"msg": USER_ROLE_EXIST}
    else:
        await repository_users.make_user_role(body.email, body.role, db)
        return {"msg": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}


