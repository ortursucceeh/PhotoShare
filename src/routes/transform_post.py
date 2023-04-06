from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.conf.messages import NOT_FOUND
from src.database.models import User
from src.database.connect_db import get_db
from src.schemas import PostResponse
from src.services.auth import auth_service
from src.tramsform_schemas import TransformCircleModel, TransformEffectModel, TransformResizeModel, TransformTextModel
from src.repository import transform_post as transform_post

router = APIRouter(prefix='/transformations', tags=["transformations"])


@router.patch("/circle/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def transform_metod_circle(post_id: int, body: TransformCircleModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await transform_post.transform_metod_circle(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.patch("/effect/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def transform_metod_effect(post_id: int, body: TransformEffectModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await transform_post.transform_metod_effect(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.patch("/resize/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def transform_metod_resize(post_id: int, body: TransformResizeModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await transform_post.transform_metod_resize(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.patch("/text/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def transform_metod_text(post_id: int, body: TransformTextModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await transform_post.transform_metod_text(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.post("/qr/{post_id}", status_code=status.HTTP_200_OK)
async def show_qr(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await transform_post.show_qr(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post

