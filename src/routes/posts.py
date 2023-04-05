from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.connect_db import get_db
from src.database.models import Post
from src.database.models import User
from src.schemas import PostModel, PostUpdate, PostResponse
from src.repository import posts as repository_posts
from src.services.auth import auth_service
from src.conf.messages import TOO_MANY_REQUESTS, NOT_FOUND
# from src.services.roles import RoleChecker
from src.database.models import User, UserRoleEnum

router = APIRouter(prefix='/posts', tags=["posts"])

# для визначення дозволу в залежності від ролі добавляємо списки дозволеності
# allowed_get_posts = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
# allowed_create_posts = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
# allowed_update_posts = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
# allowed_remove_posts = RoleChecker([UserRoleEnum.admin])


# в кожному маршруті добавляємо dependencies=[Depends(allowed_get_posts)] передаємо список тих кому дозволено

# @router.get("/", response_model=List[ResponseOwner], dependencies=[Depends(allowed_get_posts)])
# async def get_owners(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
#     owners = await repository_owners.get_owners(db)
#     return owners

@router.get("/all", response_model=List[PostResponse])
async def read_all_user_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_posts(skip, limit, current_user, db)
    return posts


@router.get("/by_id/{post_id}", response_model=PostResponse)
async def read_post_by_id(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await repository_posts.get_post(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post

@router.get("/by_title/{post_title}", response_model=List[PostResponse])
async def read_posts_with_title(post_title: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_posts_by_title(post_title, current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_user_id/{user_id}", response_model=PostResponse)
async def read_post(user_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_posts_by_user_id(user_id, current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_username/{user_name}", response_model=PostResponse)
async def read_post(user_name: int, db: Session = Depends(get_db)):
    posts = await repository_posts.get_posts_by_username(user_name, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(body: PostModel, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    return await repository_posts.create_post(body, current_user, db)


@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostModel, post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await repository_posts.update_post(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.delete("/{post_id}", response_model=PostResponse)
async def remove_post(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await repository_posts.remove_post(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post

# @router.get("/with_hashtag/{hashtag_name}", response_model=PostResponse)
# async def read_post(hashtag_name: int, db: Session = Depends(get_db)):
#     posts = await repository_posts.get_posts_with_hashtag(hashtag_name, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts

# @router.get("hashtags/all/{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db)):
#     posts = await repository_posts.get_hashtags(post_id,  db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts







# @router.get("/comments/all/{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db)):
#     posts = await repository_posts.get_comments(post_id, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts




# @router.get("/rating/{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_rating(post_id, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


##################################


# @router.get("/all", response_model=List[PostResponse], description=TOO_MANY_REQUESTS,
#             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# async def read_posts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
#                      current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_posts(skip, limit, current_user, db)
#     return posts


# @router.get("/by_id{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     post = await repository_posts.get_post(post_id, current_user, db)
#     if post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return post


# @router.get("/by_title/{post_title}", response_model=PostResponse)
# async def read_post(post_title: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_posts_by_title(post_title, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.get("/by_user_id/{user_id}", response_model=PostResponse)
# async def read_post(user_id: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_posts_by_user_id(user_id, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.get("/by_username/{user_name}", response_model=PostResponse)
# async def read_post(user_name: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_posts_by_username(user_name, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.get("/with_hashtag/{hashtag_name}", response_model=PostResponse)
# async def read_post(hashtag_name: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_posts_with_hashtag(hashtag_name, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.get("/comments/all/{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_comments(post_id, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.get("hashtags/all/{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_hashtags(post_id, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.get("/rating/{post_id}", response_model=PostResponse)
# async def read_post(post_id: int, db: Session = Depends(get_db),
#                     current_user: User = Depends(auth_service.get_current_user)):
#     posts = await repository_posts.get_rating(post_id, current_user, db)
#     if not posts:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return posts


# @router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
# async def create_post(body: PostModel, db: Session = Depends(get_db),
#                       current_user: User = Depends(auth_service.get_current_user)):
#     return await repository_posts.create_post(body, current_user, db)


# @router.put("/{post_id}", response_model=PostResponse)
# async def update_post(body: PostUpdate, post_id: int, db: Session = Depends(get_db),
#                       current_user: User = Depends(auth_service.get_current_user)):
#     post = await repository_posts.update_post(post_id, body, current_user, db)
#     if post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return post


# @router.delete("/{post_id}", response_model=PostResponse)
# async def remove_post(post_id: int, db: Session = Depends(get_db),
#                       current_user: User = Depends(auth_service.get_current_user)):
#     post = await repository_posts.remove_post(post_id, current_user, db)
#     if post is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
#     return post
