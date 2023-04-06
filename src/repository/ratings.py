from fastapi import HTTPException

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Type, Union

from starlette import status

from src.database.models import Rating, User, Post


# from src.schemas import RatingModel, UserModel, UserDb


async def create_rate(post_id: int, rate: int, db: Session, user: User) -> HTTPException | Rating:

    is_self_post = db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user.id)).first()
    already_voted = db.query(Rating).filter(and_(Rating.post_id == post_id, Rating.user_id == user.id)).first()
    post_exists = db.query(Post).filter(Post.id == post_id).first()
    if is_self_post:
        return HTTPException(status_code=status.HTTP_423_LOCKED, detail="It`s not possible vote for own post.")
    elif already_voted:
        return HTTPException(status_code=status.HTTP_423_LOCKED, detail="It`s not possible to vote twice.")
    elif post_exists:
        new_rate = Rating(post_id=post_id, rate=rate, user_id=user.id)
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate


async def delete_rate(rate_id: int, db: Session, user: User) -> Rating:
    rate = db.query(Rating).filter(Rating.id == rate_id).first()
    if rate:
        db.delete(rate)
        db.commit()
        return rate


async def show_ratings(db: Session, user: User) -> List[Rating]:
    all_ratings = db.query(Rating).all()
    return all_ratings


async def user_rate_post(user_id: int, post_id: int, db: Session, user: User) -> Rating:
    user_p_rate = db.query(Rating).filter(and_(Rating.post_id == post_id, Rating.user_id == user_id)).all()
    return user_p_rate


async def post_score(post_id: int, db: Session, user: User):
    # post = db.query(Post).filter(Post.id == post_id).first()
    # total_post_rating = post.avg_rating()

    return None #total_post_rating
