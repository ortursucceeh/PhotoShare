from typing import List

from sqlalchemy.orm import Session

from src.database.models import Hashtag, User
from src.schemas import HashtagBase


async def get_tags(skip: int, limit: int, db: Session) -> List[Hashtag]:
    return db.query(Hashtag).offset(skip).limit(limit).all()


async def get_tag(tag_id: int, db: Session) -> Hashtag:
    return db.query(Hashtag).filter(Hashtag.id == tag_id).first()



async def create_tag(body: HashtagBase, user: User, db: Session) -> Hashtag:
    # Проверяем, есть ли уже hashtag с таким названием в базе данных
    existing_tag = db.query(Hashtag).filter(Hashtag.title == body.title).first()
    if existing_tag:
        # Возвращаем уже существующий hashtag, если он есть
        return existing_tag
    else:
        # Иначе создаем новый hashtag
        tag = Hashtag(
            title=body.title,
            # user=user,
            user_id = user.id,
        )
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag
    

async def update_tag(tag_id: int, body: HashtagBase, db: Session) -> Hashtag | None:
    tag = db.query(Hashtag).filter(Hashtag.id == tag_id).first()
    if tag:
        tag .title = body.title
        db.commit()
    return tag


async def get_tags_by_user_id(user_id: int, db: Session) -> List[Hashtag]:
    return db.query(Hashtag).filter(Hashtag.user_id == user_id).all()


async def remove_tag(tag_id: int, db: Session)  -> Hashtag | None:
    tag = db.query(Hashtag).filter(Hashtag.id == tag_id).first()
    if tag:
        db.delete(tag)
        db.commit()
    return tag