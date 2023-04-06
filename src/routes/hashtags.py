# from src.services.roles import RoleChecker
# from src.database.models import User, UserRoleEnum

# # для визначення дозволу в залежності від ролі добавляємо списки дозволеності
# allowed_get_hashtags = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
# allowed_create_hashtags = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
# allowed_update_hashtags = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
# allowed_remove_hashtags = RoleChecker([UserRoleEnum.admin])


# # в кожному маршруті добавляємо dependencies=[Depends(allowed_get_hashtags)] передаємо список тих кому дозволено

# # @router.get("/", response_model=List[ResponseOwner], dependencies=[Depends(allowed_get_hashtags)])
# # async def get_owners(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
# #     owners = await repository_owners.get_owners(db)
# #     return owners


from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session

from src.database.connect_db import get_db
from src.schemas import HashtagBase, HashtagResponse
from src.repository import hashtags as repository_tags

router = APIRouter(prefix='/hashtags', tags=["hashtags"])


@router.get("/", response_model=List[HashtagResponse])
async def read_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tags = await repository_tags.get_tags(skip, limit, db)
    return tags


@router.get("/{hashtag_id}", response_model=HashtagResponse)
async def read_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.get_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.post("/", response_model=HashtagResponse)
async def create_tag(body: HashtagBase, db: Session = Depends(get_db)):
    return await repository_tags.create_tag(body, db)


@router.put("/{hashtag_id}", response_model=HashtagResponse)
async def update_tag(body: HashtagBase, tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.update_tag(tag_id, body, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag


@router.delete("/{hashtag_id}", response_model=HashtagResponse)
async def remove_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = await repository_tags.remove_tag(tag_id, db)
    if tag is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag
