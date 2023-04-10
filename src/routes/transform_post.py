from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.conf.messages import NOT_FOUND
from src.database.connect_db import get_db
from src.database.models import User
from src.schemas import PostResponse
from src.services.auth import auth_service
from src.tramsform_schemas import TransformBodyModel
from src.repository import transform_post as transform_post

router = APIRouter(prefix='/transformations', tags=["transformations"])


@router.patch("/{post_id}", response_model=PostResponse, status_code=status.HTTP_200_OK)
async def transform_metod(post_id: int, body: TransformBodyModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The transform_metod function takes a post_id and body as input,
        and returns the transformed post.
    
    :param post_id: int: Get the post id from the url
    :param body: TransformBodyModel: Get the data from the body of the request
    :param db: Session: Get the database session
    :param current_user: User: Get the user id of the current user
    :return: A post with a new body and title
    :doc-author: Trelent
    """
    post = await transform_post.transform_metod(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.post("/qr/{post_id}", status_code=status.HTTP_200_OK)
async def show_qr(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The show_qr function returns a QR code for the post with the given id.
        The user must be logged in to view this page.
    
    :param post_id: int: Find the post that is being updated
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: A post object
    :doc-author: Trelent
    """
    post = await transform_post.show_qr(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post
