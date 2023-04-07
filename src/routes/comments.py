from fastapi import APIRouter, HTTPException, Depends, status, Request

from sqlalchemy.orm import Session
from typing import List

from src.database.models import User
from src.database.connect_db import get_db
from src.schemas import CommentBase, CommentUpdate, CommentModel
from src.repository import comments as repository_comments
from src.services.auth import auth_service

from src.services.roles import RoleChecker
from src.database.models import User, UserRoleEnum

router = APIRouter(prefix='/comments', tags=["comments"])

# Role Checker-------------------------------------------------------------------------------------------

allowed_get_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_update_comments = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_remove_comments = RoleChecker([UserRoleEnum.admin])


# Operational routs-------------------------------------------------------------------------------------------
@router.post("/new/{post_id}", response_model=CommentModel, dependencies=[Depends(allowed_create_comments)])
async def create_comment(post_id: int, body: CommentBase, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_comment function creates a new comment for the post with the given id. The function takes in a
    CommentBase object, which contains all of the information needed to create a new comment. It also takes in an
    optional db Session and current_user User object, which are used by dependency injection.

    :param post_id: int: Specify the post that the comment is for
    :param body: CommentBase: Get the body of the comment from the request
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user from the database
    :return: The newly created comment
    """
    new_comment = await repository_comments.create_comment(post_id, body, db, current_user)
    return new_comment


@router.put("/edit/{comment_id}", response_model=CommentUpdate, dependencies=[Depends(allowed_update_comments)])
async def edit_comment(comment_id: int, body: CommentBase, db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The edit_comment function allows a user to edit their own comment. The function takes in the comment_id, body,
    db and current_user as parameters. It then calls the edit_comment function from repository/comments.py which
    returns an edited comment object if successful or None otherwise.

    :param comment_id: int: Identify the comment that is to be deleted
    :param body: CommentBase: Pass the body of the comment to be edited
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Check if the user is authorized to delete the comment
    :return: A comment object
    """
    edited_comment = await repository_comments.edit_comment(comment_id, body, db, current_user)
    if edited_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or not available.")
    return edited_comment


@router.delete("/delete/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_remove_comments)])
async def delete_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The delete_comment function deletes a comment from the database.
        The function takes in an integer representing the id of the comment to be deleted,
        and returns a dictionary containing information about that comment.

    :param comment_id: int: Identify the comment that is to be deleted
    :param db: Session: Access the database
    :param current_user: User: Get the current user from the auth_service
    :return: A comment object
    """
    deleted_comment = await repository_comments.delete_comment(comment_id, db, current_user)
    if deleted_comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or not available.")
    return deleted_comment


# Query routs-------------------------------------------------------------------------------------------

@router.get("/single/{comment_id}", response_model=CommentModel, dependencies=[Depends(allowed_get_comments)])
async def single_comment(comment_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The single_comment function is used to retrieve a single comment from the database.
        The function takes in an integer representing the id of the comment, and returns a Comment object.

    :param comment_id: int: Specify the comment id of the comment to be deleted
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user_id of the current logged in user
    :return: A single comment
    """
    comment = await repository_comments.show_single_comment(comment_id, db, current_user)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exact comment not found.")
    return comment


@router.get("/all_in_post/{post_id}", response_model=List[CommentModel], dependencies=[Depends(allowed_get_comments)])
async def post_all_comments(post_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)
                            ):
    """
    The post_all_comments function returns all comments for a given post. The function takes in the post_id as an
    argument and uses it to query the database for all comments associated with that id. If no such comment exists,
    then a 404 error is raised.

    :param post_id: int: Get the comments for a specific post
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the current user
    :return: A list of comments for a given post
    """
    comments = await repository_comments.show_post_comments(post_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments or post not found.")
    return comments


@router.get("/by_author/{user_id}", response_model=List[CommentModel], dependencies=[Depends(allowed_get_comments)])
async def by_user_comments(user_id: int, db: Session = Depends(get_db),
                           current_user: User = Depends(auth_service.get_current_user)
                           ):
    """
    The by_user_comments function returns all comments made by a user.
        ---
        get:
          summary: Returns all comments made by a user.
          tags: [comments]

    :param user_id: int: Specify the user_id of the author
    :param db: Session: Access the database
    :param current_user: User: Get the current user
    :return: The comments of the user
    """
    comments = await repository_comments.show_user_comments(user_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments or author does not exist.")
    return comments


@router.get("/post_by_author/{user_id}/{post_id}", response_model=List[CommentModel],
            dependencies=[Depends(allowed_get_comments)])
async def by_user_post_comments(user_id: int, post_id: int, db: Session = Depends(get_db),
                                current_user: User = Depends(auth_service.get_current_user)
                                ):
    """
    The by_user_post_comments function returns a list of comments for a given user and post.
        The function takes in the following parameters:
            - user_id: int, the id of the user whose comments are being retrieved.
            - post_id: int, the id of the post whose comments are being retrieved.

    :param user_id: int: Get the user_id of the user who made a comment
    :param post_id: int: Get the comments of a specific post
    :param db: Session: Get the database session
    :param current_user: User: Check if the user is logged in
    :return: A list of comments
    """
    comments = await repository_comments.show_user_post_comments(user_id, post_id, db)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments or user not found.")
    return comments
