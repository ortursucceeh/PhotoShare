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
async def create_post(request: Request, title: str = Form(None), descr: str = Form(None),
                    hashtags: List = Form(None), file: UploadFile = File(None),
                    db: Session = Depends(get_db), 
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_post function creates a new post in the database.
        The function takes in a title, description, hashtags and an image file as parameters.
        It then uses these to create a new post object which is added to the database.
    
    :param request: Request: Get the request object
    :param title: str: Get the title of the post from the request body
    :param descr: str: Get the description of the post from the request
    :param hashtags: List: Get the list of hashtags from the request body
    :param file: UploadFile: Get the file from the request
    :param db: Session: Get the database session, which is used to perform sql queries
    :param current_user: User: Get the user who is currently logged in
    :return: A dict, which is a json object
    """
    return await repository_posts.create_post(request, title, descr, hashtags, file, db, current_user)


@router.get("/my_posts", response_model=List[PostResponse])
async def read_all_user_posts(skip: int = 0, limit: int = 100, current_user: User = Depends(auth_service.get_current_user), 
                              db: Session = Depends(get_db)):
    """
    The read_all_user_posts function returns all posts for a given user.
        The function takes in the following parameters:
            skip (int): The number of posts to skip before returning results. Default is 0.
            limit (int): The maximum number of posts to return per page. Default is 100, max is 1000.
    
    :param skip: int: Skip a number of posts
    :param limit: int: Limit the number of posts returned
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of posts
    """
    posts = await repository_posts.get_my_posts(skip, limit, current_user, db)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/all", response_model=List[PostResponse], dependencies=[Depends(allowed_get_all_posts)])
async def read_all_posts(skip: int = 0, limit: int = 100,
            current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The read_all_posts function returns all posts in the database.
        ---
        get:
          summary: Returns all posts in the database.
          description: Returns a list of all posts in the database, with optional skip and limit parameters to paginate results.
          tags: [posts]
          responses:
            '200': # HTTP status code 200 is returned when successful (OK) 
    
    :param skip: int: Skip the first n posts
    :param limit: int: Limit the number of posts returned
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: A list of posts
    """
    posts = await repository_posts.get_all_posts(skip, limit, db)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_id/{post_id}", response_model=PostResponse)
async def read_post_by_id(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_post_by_id function returns a post by its id.
        If the user is not logged in, it will return an error message.
        If the user is logged in but does not have access to this post, it will return an error message.
    
    :param post_id: int: Get the post by id
    :param db: Session: Pass the database session to the function
    :param current_user: User: Check if the user is authorized to access the post
    :return: A post object, as defined in the models
    """
    post = await repository_posts.get_post_by_id(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.get("/by_title/{post_title}", response_model=List[PostResponse])
async def read_posts_with_title(post_title: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_posts_with_title function is used to read posts with a given title.
        The function takes in the post_title as an argument and returns all posts that match the title.
    
    :param post_title: str: Pass the title of the post to be searched for
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user, and the db: session parameter is used to get a database session
    :return: A list of posts
    """
    posts = await repository_posts.get_posts_by_title(post_title, current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_user_id/{user_id}", response_model=List[PostResponse])
async def read_posts_by_user_id(user_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_posts_by_user_id function returns all posts by a user with the given id.
        The function takes in an integer user_id and returns a list of Post objects.
    
    :param user_id: int: Specify the user_id of the posts that we want to retrieve
    :param db: Session: Pass the database connection to the repository
    :param current_user: User: Get the user that is currently logged in
    :return: A list of posts
    """
    posts = await repository_posts.get_posts_by_user_id(user_id, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_username/{user_name}", response_model=List[PostResponse])
async def read_post_with_user_username(user_name: str, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_post function is used to read a post by username.
        The function takes in the user_name and db as parameters,
        and returns posts.
    
    :param user_name: str: Get the username of the user whose posts we want to read
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of posts, which is the same as what i am trying to return in my test
    """
    posts = await repository_posts.get_posts_by_username(user_name, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/with_hashtag/{hashtag_name}", response_model=List[PostResponse])
async def read_post_with_hashtag(hashtag_name: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_post_with_hashtag function returns a list of posts that contain the hashtag_name.
        The function takes in a hashtag_name and an optional db Session object, which is used to connect to the database.
        It also takes in an optional current_user User object, which is used for authentication purposes.
    
    :param hashtag_name: str: Get the hashtag name from the url path
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: A list of posts that contain the hashtag
    """
    posts = await repository_posts.get_posts_with_hashtag(hashtag_name, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/comments/all/{post_id}", response_model=List[CommentModel])
async def read_post_comments(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_post_comments function returns a list of comments for the specified post.
        The function takes in an integer representing the post_id and returns a list of comments.
    
    :param post_id: int: Get the post_id from the url
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the user details of the current logged in user
    :return: A list of comments for a post
    """
    posts = await repository_posts.get_post_comments(post_id, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/by_keyword/{keyword}", response_model=List[PostResponse])
async def read_post_by_keyword(keyword: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_post_by_keyword function returns a list of posts that contain the keyword in their title or body.
    
    :param keyword: str: Specify the keyword that we want to search for
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user who is logged in
    :return: A list of posts
    """
    posts = await repository_posts.get_post_by_keyword(keyword, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts

@router.put("/{post_id}", response_model=PostResponse)
async def update_post(body: PostUpdate, post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_post function updates a post in the database.
        The function takes three arguments:
            - body: A PostUpdate object containing the new values for the post.
            - post_id: An integer representing the id of an existing post to update.
            - db (optional): A Session object used to connect to and query a database, defaults to None if not provided. 
                If no session is provided, one will be created using get_db().
    
    :param body: PostUpdate: Get the data from the request body
    :param post_id: int: Find the post in the database
    :param db: Session: Pass the database session to the repository
    :param current_user: User: Check if the user is authorized to update the post
    :return: A post object
    """
    post = await repository_posts.update_post(post_id, body, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post


@router.delete("/{post_id}", response_model=PostResponse)
async def remove_post(post_id: int, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_post function removes a post from the database.
        The function takes in an integer representing the id of the post to be removed,
        and returns a dictionary containing information about that post.
    
    :param post_id: int: Specify the post to be deleted
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Check if the user is logged in
    :return: A post object, but the remove_post function in repository_posts returns none
    """
    post = await repository_posts.remove_post(post_id, current_user, db)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return post














