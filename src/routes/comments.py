from fastapi import APIRouter, HTTPException, Depends, status, Request

from sqlalchemy.orm import Session
from typing import List

from src.database.models import User
from src.database.connect_db import get_db
from src.schemas import CommentBase, CommentUpdate, CommentModel
from src.repository import comments as repository_comments
from src.services.auth import auth_service
from src.conf import messages as message

from src.services.roles import RoleChecker
from src.database.models import User, UserRoleEnum

router = APIRouter(prefix='/comments', tags=["comments"])

# Role Checker-------------------------------------------------------------------------------------------

allowed_get_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_update_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_remove_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])


# Operational routs-------------------------------------------------------------------------------------------
@router.post("/new/{post_id}", response_model=CommentModel, dependencies=[Depends(allowed_create_comments)])
async def create_comment(post_id: int, body: CommentBase, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    new_comment = await repository_comments.create_comment(post_id, body, db, current_user)
    return new_comment


@router.put("/edit/{comment_id}", response_model=CommentUpdate, dependencies=[Depends(allowed_update_comments)])
async def edit_comment(comment_id: int, body: CommentBase, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    edited_comment = await repository_comments.edit_comment(comment_id, body, db, current_user)
    if edited_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return edited_comment


@router.delete("/delete/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_remove_comments)])
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    deleted_comment = await repository_comments.delete_comment(comment_id, db, current_user)
    if deleted_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return deleted_comment


@router.get("/single/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_get_comments)])
async def single_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.show_single_comment(comment_id, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comment


@router.get("/by_author/{user_id}", response_model=List[CommentModel], dependencies=[Depends(allowed_get_comments)])
async def by_user_comments(user_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    comments = await repository_comments.show_user_comments(user_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comments


@router.get("/post_by_author/{user_id}/{post_id}", response_model=List[CommentModel],
            dependencies=[Depends(allowed_get_comments)])
async def by_user_post_comments(user_id: int, post_id: int, db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    comments = await repository_comments.show_user_post_comments(user_id, post_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comments
