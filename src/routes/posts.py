from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request
from typing import List
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.connect_db import get_db
from src.database.models import User, UserRoleEnum
from src.schemas import CommentModel, PostModel, PostResponse, PostUpdate
from src.repository import posts as repository_posts
from src.services.auth import auth_service
from src.conf.messages import NOT_FOUND
from src.services.roles import RoleChecker
# from src.services.roles import RoleChecker

router = APIRouter(prefix='/posts', tags=["posts"])

# для визначення дозволу в залежності від ролі добавляємо списки дозволеності
allowed_get_all_posts = RoleChecker([UserRoleEnum.admin])



@router.post("/new/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(request: Request, title: str = Form(None), descr: str = Form(None), hashtags: List = Form(None),
file: UploadFile = File(None), db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    return await repository_posts.create_post(request, title, descr, hashtags, file, db, current_user)


@router.get("/my_posts", response_model=List[PostResponse])
async def read_all_user_posts(skip: int = 0, limit: int = 100, current_user: User = Depends(auth_service.get_current_user), 
                              db: Session = Depends(get_db)):
    posts = await repository_posts.get_my_posts(skip, limit, current_user, db)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/all", response_model=List[PostResponse], dependencies=[Depends(allowed_get_all_posts)])
async def read_all_posts(skip: int = 0, limit: int = 100,
            current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    posts = await repository_posts.get_all_posts(skip, limit, db)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_id/{post_id}", response_model=PostResponse)
async def read_post_by_id(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    post = await repository_posts.get_post_by_id(post_id, current_user, db)
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


@router.get("/by_user_id/{user_id}", response_model=List[PostResponse])
async def read_posts_by_user_id(user_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_posts_by_user_id(user_id, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_username/{user_name}", response_model=List[PostResponse])
async def read_post(user_name: str, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_posts_by_username(user_name, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/with_hashtag/{hashtag_name}", response_model=List[PostResponse])
async def read_post_with_hashtag(hashtag_name: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_posts_with_hashtag(hashtag_name, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/comments/all/{post_id}", response_model=List[CommentModel])
async def read_post_comments(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.get_post_comments(post_id, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts

@router.get("/by_keyword/{keyword}", response_model=List[PostResponse])
async def read_post_with_hashtag(keyword: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    posts = await repository_posts.searcher(keyword, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostUpdate, post_id: int, db: Session = Depends(get_db),
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














