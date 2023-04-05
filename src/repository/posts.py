from typing import List
from datetime import datetime

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.database.models import Post, Hashtag, User # Rating, Comment
from src.schemas import PostModel, PostUpdate

async def get_user_posts(skip: int, limit: int, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(Post.user_id == user.id).offset(skip).limit(limit).all()

async def get_post(post_id: int, user: User, db: Session) -> Post:
    return db.query(Post).filter(and_(Post.user_id == user.id, Post.id == post_id)).first()

async def create_post(body: PostModel, user: User,  db: Session) -> Post:
    hashtags = db.query(Hashtag).filter(and_(Hashtag.id.in_(body.hashtags))).all()
    post = Post(
        image_url=body.image_url,
        title=body.title,
        descr=body.descr,
        hashtags=hashtags,
        user=user,
        done=True
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


async def update_post(post_id: int, body: PostUpdate, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter(and_(Post.user_id == user.id, Post.id == post_id)).first()
    if post:
        hashtags = db.query(Hashtag).filter(and_(Hashtag.id.in_(body.hashtags))).all()
        post.image_url = body.image_url
        post.title = body.title
        post.descr = body.descr
        post.hashtags = hashtags
        post.updated_at = datetime.now()
        post.user=user
        post.done = True
        
        db.commit()
    return post


async def remove_post(post_id: int, user: User, db: Session) -> Post | None:
    post = db.query(Post).filter(and_(Post.user_id == user.id, Post.id == post_id)).first()
    if post:
        db.delete(post)
        db.commit()
    return post

async def get_posts_with_hashtag(hashtag_name: str, db: Session) -> Post: #
    return db.query(Post).filter(and_(Hashtag.title.like(f'%{hashtag_name}%'))).all()


async def get_hashtags(post_id: int, db: Session) -> Hashtag: #
    return db.query(Hashtag).filter(and_(Hashtag.post == post_id)).all()


# шукати по всім юзерам, без прив'язки до поточного --------------------
# def get_all_posts
async def get_posts_by_title(post_title: str, user: User, db: Session) -> List[Post]:
    return db.query(Post).filter(and_(Post.user_id == user.id, func.lower(Post.title).like(f'%{post_title.lower()}%'))).all()



async def get_posts_by_user_id(user_id: int, user: User, db: Session) -> Post:
    return db.query(Post).filter(and_(Post.user_id == user.id, Post.user_id == user_id)).all()


async def get_posts_by_username(user_name: str, user: User, db: Session) -> Post: #
    return db.query(Post).filter(and_(Post.user_id == user.id, func.lower(user.username).like(f'%{user_name.lower()}%'))).all()
# ----------------------------------------------------------------




# async def get_comments(post_id: int, user: User, db: Session) -> List[Comment]: #
#     return db.query(Comment).filter(and_(Comment.post == post_id, Comment.user_id == user.id)).all()




# async def get_rating(post_id: int, user: User, db: Session) -> Rating:
#     return db.query(Rating).filter(and_(Rating.post == post_id, Rating.user_id == user.id)).first()





###########################33

# async def get_posts(skip: int, limit: int, user: User, db: Session) -> List[Post]:
#     return db.query(Post).filter(Post.user_id == user.id).offset(skip).limit(limit).all()


# async def get_post(post_id: int, user: User, db: Session) -> Post:
#     return db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user.id)).first()


# async def get_posts_by_title(post_title: str, user: User, db: Session) -> List[Post]:
#     return db.query(Post).filter(and_(Post.user_id == user.id, Post.title.like(f'%{post_title}%'))).all()


# async def get_posts_by_user_id(user_id: int, user: User, db: Session) -> Post:
#     return db.query(Post).filter(and_(Post.user_id == user.id, Post.user_id.like(f'%{user_id}%'))).all()


# async def get_posts_by_username(user_name: str, user: User, db: Session) -> Post: #
#     return db.query(Post).filter(and_(Post.user_id == user.id, user.username.like(f'%{user_name}%'))).all()


# async def get_posts_with_hashtag(hashtag_name: str, user: User, db: Session) -> Post: #
#     return db.query(Post).filter(and_(Post.user_id == user.id, Hashtag.title.like(f'%{hashtag_name}%'))).all()


# async def get_comments(post_id: int, user: User, db: Session) -> List[Comment]: #
#     return db.query(Comment).filter(and_(Comment.post == post_id, Comment.user_id == user.id)).all()


# async def get_hashtags(post_id: int, user: User, db: Session) -> Hashtag: #
#     return db.query(Hashtag).filter(and_(Hashtag.post == post_id, Hashtag.user_id == user.id)).all()


# async def get_rating(post_id: int, user: User, db: Session) -> Rating:
#     return db.query(Rating).filter(and_(Rating.post == post_id, Rating.user_id == user.id)).first()


# async def create_post(body: PostModel, user: User, db: Session) -> Post:
#     hashtags = db.query(Hashtag).filter(and_(Hashtag.id.in_(body.hashtags), Hashtag.user_id == user.id)).all()
#     rating = db.query(Rating).filter(and_(Rating.id.in_(body.rating), Rating.user_id == user.id)).all()
#     post = post(title=body.title, descr=body.descr, hashtags=hashtags, rating=rating, user=user)
#     db.add(post)
#     db.commit()
#     db.refresh(post)
#     return post


# async def update_post(post_id: int, body: PostUpdate, user: User, db: Session) -> Post | None:
#     post = db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user.id)).first()
#     if post:
#         hashtags = db.query(Hashtag).filter(and_(Hashtag.id.in_(body.hashtags), Post.user_id == user.id)).all()
#         rating = db.query(Rating).filter(and_(Rating.id.in_(body.rating), Rating.user_id == user.id)).all()
#         post.image_url = body.image_url
#         post.title = body.title
#         post.descr = body.descr
#         post.done = body.done
#         post.hashtags = hashtags
#         post.rating = rating
#         db.commit()
#     return post


# async def remove_post(post_id: int, user: User, db: Session) -> Post | None:
#     post = db.query(Post).filter(and_(Post.id == post_id, Post.user_id == user.id)).first()
#     if post:
#         db.delete(post)
#         db.commit()
#     return post