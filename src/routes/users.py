from fastapi import APIRouter, Depends, status, UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.connect_db import get_db
from src.database.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings, init_cloudinary
from src.schemas import UserDb

router = APIRouter(prefix="/users", tags=["users"])


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