import cloudinary
import cloudinary.uploader

from typing import List
from datetime import datetime
from fastapi import Request, UploadFile
from faker import Faker
from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.conf.config import init_cloudinary
from src.database.models import Post, Hashtag, User, Comment, Rating, UserRoleEnum
from src.schemas import PostModel, PostUpdate


async def get_all_posts(skip: int, limit: int, db: Session) -> List[Post]:
    return db.query(Post).offset(skip).limit(limit).offset(skip).limit(limit).all()


async def get_my_posts(skip: int, limit: int, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(Post.user_id == user.id).offset(skip).limit(limit).all()


async def get_post_by_id(post_id: int, user: User, db: Session) -> Post:
    post = db.query(Post).filter(and_(Post.user_id == user.id, Post.id == post_id)).first()
    return post


async def get_posts_by_title(post_title: str, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(func.lower(Post.title).like(f'%{post_title.lower()}%')).all()


async def get_posts_by_user_id(user_id: int, db: Session) -> List[Post]:
    return db.query(Post).filter(Post.user_id == user_id).all()


async def get_posts_by_username(user_name: str, db: Session) -> List[Post]: 
    searched_user = db.query(User).filter(func.lower(User.username).like(f'%{user_name.lower()}%')).first()
    return db.query(Post).filter(Post.user_id == searched_user.id).all()


async def get_posts_with_hashtag(hashtag_name: str, db: Session) -> List[Post]: 
    return db.query(Post).join(Post.tags).filter(Hashtag.title == hashtag_name).all()


async def get_post_comments(post_id: int, db: Session) -> List[Comment]: 
    return db.query(Comment).filter(Comment.post_id == post_id).all()


def get_hashtags(hashtag_titles: list, user: User, db: Session):
    tags = []
    for tag_title in hashtag_titles:
        tag = db.query(Hashtag).filter(Hashtag.title == tag_title).first()
        if not tag:
            tag = Hashtag(
            title=tag_title,
            user_id = user.id,
            )
            db.add(tag)
            db.commit()
            db.refresh(tag)
        tags.append(tag)
    return tags


async def create_post(request: Request, title: str, descr: str, hashtags: List, file: UploadFile, db: Session, current_user: User) -> Post:
    public_id = Faker().first_name()
    init_cloudinary()
    cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill')
    hashtagss = get_hashtags(hashtags[0].split(","), current_user, db)
    
    post = Post(
        image_url = url,
        title = title,
        descr = descr,
        created_at = datetime.now(),
        user_id = current_user.id,
        hashtags = hashtagss,
        public_id = public_id,
        done=True
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


async def update_post(post_id: int, body: PostUpdate, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter(Post.id == post_id).first()
    
    if post:
        if user.role == UserRoleEnum.admin or post.user_id == user.id:
            hashtags = get_hashtags(body.hashtags, user, db)

            post.title = body.title
            post.descr = body.descr
            post.hashtags = hashtags
            post.updated_at = datetime.now()
            post.done = True
            db.commit()
    return post


async def remove_post(post_id: int, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post:
        if user.role == UserRoleEnum.admin or post.user_id == user.id:
            init_cloudinary()
            cloudinary.uploader.destroy(post.public_id)
            db.delete(post)
            db.commit()
    return post


# async def get_rating(post_id: int, user: User, db: Session) -> Rating:
#     return db.query(Rating).filter(and_(Rating.post == post_id, Rating.user_id == user.id)).first()

# ----------------------------------------------------------------









