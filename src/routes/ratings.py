from fastapi import APIRouter, HTTPException, Depends, status, Request, Path

from sqlalchemy.orm import Session
from typing import List, Union

from src.database.connect_db import get_db
from src.schemas import RatingModel
from src.repository import ratings as repository_ratings
from src.services.auth import auth_service
from src.services.roles import RoleChecker
from src.database.models import User, UserRoleEnum

router = APIRouter(prefix='/ratings', tags=["ratings"])

# Role Checker-------------------------------------------------------------------------------------------

allowed_get_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_remove_ratings = RoleChecker([UserRoleEnum.admin])


# Operational routs-------------------------------------------------------------------------------------------
@router.post("/posts/{post_id}/{rate}", response_model=RatingModel, dependencies=[Depends(allowed_create_ratings)])
async def create_rate(post_id: int, rate: int = Path(description="From one to five stars of rating.", ge=1, le=5),
                      db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_rate function creates a new rate for the post with the given ID. The function takes in an integer
    value from 1 to 5, and returns a JSON object containing information about the newly created rate.

    :param post_id: int: Get the post id from the url
    :param rate: int: Set the rating of a post
    :param ge: Specify the minimum value of a number
    :param le: Set the maximum value of the rate
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: The new rate
    """
    new_rate = await repository_ratings.create_rate(post_id, rate, db, current_user)
    if new_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No post with this ID.")
    return new_rate


@router.delete("/delete/{rate_id}", response_model=RatingModel, dependencies=[Depends(allowed_remove_ratings)])
async def delete_rate(rate_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)
                      ):
    """
    The delete_rate function deletes a rate from the database.
        The function takes in an integer, which is the id of the rate to be deleted.
        It also takes in a Session object and a User object as parameters,
        which are used to access and delete data from the database.

    :param rate_id: int: Get the rate_id from the url
    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the auth_service
    :return: A rate object
    """
    deleted_rate = await repository_ratings.delete_rate(rate_id, db, current_user)
    if deleted_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found or not available.")
    return deleted_rate


@router.get("/all", response_model=List[RatingModel], dependencies=[Depends(allowed_get_ratings)])
async def all_rates(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The all_rates function returns all the ratings in the database.


    :param db: Session: Get the database connection
    :param current_user: User: Get the current user from the database
    :return: A list of all the ratings in the database
    """
    comments = await repository_ratings.show_ratings(db, current_user)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ratings doesn`t not found.")
    return comments


@router.get("/user_post/{user_id}/{post_id}", response_model=RatingModel,
            dependencies=[Depends(allowed_get_ratings)])
async def user_rate_post(user_id: int, post_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)
                         ):
    """
    The user_rate_post function allows a user to rate a post.
        The function takes in the user_id and post_id as parameters, along with the database session and current user.
        If no rating is found, an HTTPException is raised.

    :param user_id: int: Identify the user who is rating a post
    :param post_id: int: Get the post id
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user_id from the token
    :return: A rating object
    """
    rate = await repository_ratings.user_rate_post(user_id, post_id, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found.")
    return rate


@router.get("/post/{post_id}", response_model=dict, dependencies=[Depends(allowed_get_ratings)])
async def post_rating(post_id: int, current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)
                      ):
    """
    The post_rating function is used to rate a post.
        The function takes in the post_id and current_user as parameters,
        and returns the rating of that particular user on that particular post.

    :param post_id: int: Identify the post that is being rated
    :param current_user: User: Get the current user from the database
    :param db: Session: Access the database
    :return: A rating object
    :doc-author: Trelent
    """
    rate = await repository_ratings.post_score(post_id, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found.")
    return rate
