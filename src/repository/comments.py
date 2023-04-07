from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from typing import List

from src.database.models import User, Comment
from src.schemas import CommentBase


# Operational def_s-------------------------------------------------------------------------------------------

async def create_comment(post_id: int, body: CommentBase, db: Session, user: User) -> Comment:
    """
    The create_comment function creates a new comment in the database.
        Args:
            post_id (int): The id of the post to which this comment belongs.
            body (CommentBase): A CommentBase object containing information about the new comment.
            db (Session): An open database session for making queries and committing changes to the database.

    :param post_id: int: Specify the post that the comment is being added to
    :param body: CommentBase: Get the text of the comment from the request body
    :param db: Session: Access the database
    :param user: User: Get the user_id from the logged in user
    :return: The new comment
    """
    new_comment = Comment(text=body.text, post_id=post_id, user_id=user.id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


async def edit_comment(comment_id: int, body: CommentBase, db: Session, user: User) -> Comment | None:
    """
    The edit_comment function takes in a comment_id, body, db and user. The function then queries the database for a
    comment with the given id and user_id. If such a comment exists, it updates its text to that of the body's text
    field and sets its update status to True. Finally it commits these changes to the database.

    :param comment_id: int: Identify the comment that needs to be deleted
    :param body: CommentBase: Get the text from the body of the request
    :param db: Session: Access the database
    :param user: User: Make sure that the comment is being edited by the user who created it
    :return: A comment object if the comment was successfully edited
    """
    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if comment:
        comment.text = body.text
        comment.updated_at = func.now()
        comment.update_status = True
    db.commit()
    return comment


async def delete_comment(comment_id: int, db: Session, user: User) -> None:
    """
    The delete_comment function deletes a comment from the database. Args: comment_id (int): The id of the comment to
    be deleted. db (Session): A connection to the database.  This is used for querying and deleting comments from the
    database. user (User): The user who is making this request, which will be used to verify that they are authorized
    to delete this particular comment.

    :param comment_id: int: Specify which comment to delete
    :param db: Session: Access the database
    :param user: User: Check if the user is the owner of the comment
    :return: A comment object
    """
    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment

# Query def_s-------------------------------------------------------------------------------------------


async def show_single_comment(comment_id: int, db: Session, user: User) -> Comment | None:
    """
    The show_single_comment function returns a single comment from the database. Args: comment_id (int): The id of
    the comment to be returned. db (Session): A connection to the database.  This is provided by FastAPI when it
    calls this function, so you don't need to worry about it! user (User): The currently logged in user,
    as determined by FastAPI's authentication system.  Again, this is provided for you automatically and does not
    need to be passed in explicitly!

    :param comment_id: int: Specify the id of the comment to be retrieved
    :param db: Session: Access the database
    :param user: User: Retrieve the user's comments
    :return: A single comment
    """
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()


async def show_post_comments(comment_id: int, db: Session) -> List[Comment] | None:
    """
    The show_post_comments function returns a list of comments for a given post_id.
        Args:
            comment_id (int): The id of the post to return comments for.
            db (Session): A database session object used to query the database.

    :param comment_id: int: Filter the comments by post_id
    :param db: Session: Pass the database session to the function
    :return: A list of comments that are associated with a post
    """
    return db.query(Comment).filter(Comment.post_id == comment_id).all()


async def show_user_comments(user_id: int, db: Session) -> List[Comment] | None:
    """
    The show_user_comments function returns a list of comments made by the user with the given id.
        If no such user exists, it returns None.

    :param user_id: int: Filter the comments by user_id
    :param db: Session: Pass the database session to the function
    :return: A list of comments for a given user_id
    """
    return db.query(Comment).filter(Comment.user_id == user_id).all()


async def show_user_post_comments(user_id: int, post_id: int, db: Session) -> List[Comment] | None:
    """
    The show_user_post_comments function returns a list of comments for a given user and post.
        Args:
            user_id (int): The id of the user whose comments are being retrieved.
            post_id (int): The id of the post whose comments are being retrieved.

    :param user_id: int: Filter the comments by user_id
    :param post_id: int: Filter the comments by post_id
    :param db: Session: Pass the database session to the function
    :return: A list of comment objects
    """
    return db.query(Comment).filter(and_(Comment.id == post_id, Comment.user_id == user_id)).all()
