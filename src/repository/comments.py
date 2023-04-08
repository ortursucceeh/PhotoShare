from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from src.database.models import User, Comment, UserRoleEnum
from src.schemas import CommentBase


async def create_comment(post_id: int, body: CommentBase, db: Session, user: User) -> Comment:
    new_comment = Comment(text=body.text, post_id=post_id, user_id=user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


async def edit_comment(comment_id: int, body: CommentBase, db: Session, user: User) -> Comment | None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if user.role in [UserRoleEnum.admin, UserRoleEnum.moder] or comment.user_id == user.id:
        if comment:
            comment.text = body.text
            comment.updated_at = func.now()
            comment.update_status = True
            db.commit()
    return comment


async def delete_comment(comment_id: int, db: Session, user: User) -> None:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment


async def show_single_comment(comment_id: int, db: Session, user: User) -> Comment | None:
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()


async def show_user_comments(user_id: int, db: Session) -> List[Comment] | None:
    return db.query(Comment).filter(Comment.user_id == user_id).all()


async def show_user_post_comments(user_id: int, post_id: int, db: Session) -> List[Comment] | None:
    return db.query(Comment).filter(and_(Comment.post_id == post_id, Comment.user_id == user_id)).all()
