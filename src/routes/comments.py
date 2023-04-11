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


allowed_get_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_update_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_remove_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])


@router.post("/new/{post_id}", response_model=CommentModel, dependencies=[Depends(allowed_create_comments)])
async def create_comment(post_id: int, body: CommentBase, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_comment function creates a new comment for the post with the given id.
        The body of the comment is passed in as JSON data, and must contain a &quot;body&quot; field.
        The user who created this comment will be set to current_user.
    
    :param post_id: int: Specify the post that the comment is being created for
    :param body: CommentBase: Pass the data from the request body to the function
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A comment object, which is then serialized as json
    """
    new_comment = await repository_comments.create_comment(post_id, body, db, current_user)
    return new_comment


@router.put("/edit/{comment_id}", response_model=CommentUpdate, dependencies=[Depends(allowed_update_comments)])
async def edit_comment(comment_id: int, body: CommentBase, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The edit_comment function allows a user to edit their own comment.
        The function takes in the comment_id, body and db as parameters.
        It then calls the edit_comment function from repository_comments which returns an edited comment object if successful or None otherwise. 
        If it is unsuccessful, it raises a 404 error with detail message COMM_NOT_FOUND.
    
    :param comment_id: int: Identify the comment to be edited
    :param body: CommentBase: Pass the comment body to the edit_comment function
    :param db: Session: Get the database session
    :param current_user: User: Get the user who is currently logged in
    :return: None, but the function expects a commentbase object
    """
    edited_comment = await repository_comments.edit_comment(comment_id, body, db, current_user)
    if edited_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return edited_comment


@router.delete("/delete/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_remove_comments)])
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The delete_comment function deletes a comment from the database.
        The function takes in an integer representing the id of the comment to be deleted,
        and returns a dictionary containing information about that comment.
    
    :param comment_id: int: Specify the comment that is to be deleted
    :param db: Session: Get the database session from the dependency
    :param current_user: User: Check if the user is logged in
    :return: The deleted comment
    """
    deleted_comment = await repository_comments.delete_comment(comment_id, db, current_user)
    if deleted_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return deleted_comment


@router.get("/single/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_get_comments)])
async def single_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The single_comment function returns a single comment from the database.
        The function takes in an integer representing the id of the comment to be returned,
        and two optional parameters: db and current_user. If no db is provided, it will use 
        get_db() to create a new connection with our database. If no current user is provided,
        it will use auth_service's get_current_user() function to retrieve one.
    
    :param comment_id: int: Pass the comment id to the function
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user from the database
    :return: The comment object, but i want to return the comment_id
    """
    comment = await repository_comments.show_single_comment(comment_id, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comment


@router.get("/by_author/{user_id}", response_model=List[CommentModel], dependencies=[Depends(allowed_get_comments)])
async def by_user_comments(user_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)):
    """
    The by_user_comments function returns all comments made by a user.
        Args:
            user_id (int): The id of the user whose comments are to be returned.
            db (Session, optional): SQLAlchemy Session. Defaults to Depends(get_db).
            current_user (User, optional): User object for the currently logged in user. Defaults to Depends(auth_service.get_current_user).
        Returns:
            List[Comment]: A list of Comment objects representing all comments made by a given user.
    
    :param user_id: int: Specify the user_id of the user whose comments we want to see
    :param db: Session: Pass the database session to the function
    :param current_user: User: Check if the user is logged in
    :return: A list of comments
    """
    comments = await repository_comments.show_user_comments(user_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comments


@router.get("/post_by_author/{user_id}/{post_id}", response_model=List[CommentModel],
            dependencies=[Depends(allowed_get_comments)])
async def by_user_post_comments(user_id: int, post_id: int, db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)):
    """
    The by_user_post_comments function returns all comments for a given user and post.
        Args:
            user_id (int): The id of the user whose comments are being retrieved.
            post_id (int): The id of the post whose comments are being retrieved.
        Returns:
            A list containing all comment objects associated with a given user and post.
    
    :param user_id: int: Specify the user_id of the user whose comments we want to retrieve
    :param post_id: int: Get the comments for a specific post
    :param db: Session: Access the database
    :param current_user: User: Get the current user who is logged in
    :return: A list of comments that belong to a post
    """
    comments = await repository_comments.show_user_post_comments(user_id, post_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return comments
