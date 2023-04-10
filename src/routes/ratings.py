from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Request, Path
from sqlalchemy.orm import Session

from src.database.connect_db import get_db
from src.schemas import RatingModel, PostResponse
from src.repository import ratings as repository_ratings
from src.services.auth import auth_service
from src.services.roles import RoleChecker
from src.database.models import User, UserRoleEnum
from src.conf import messages as message

router = APIRouter(prefix='/ratings', tags=["ratings"])

# Role Checker-------------------------------------------------------------------------------------------

allowed_get_all_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_create_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_edit_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_remove_ratings = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder])
allowed_user_post_rate = RoleChecker([UserRoleEnum.admin])
allowed_commented_by_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_POST_ID)
    return new_rate


@router.put("/edit/{rate_id}/{new_rate}", response_model=RatingModel, dependencies=[Depends(allowed_edit_ratings)])
async def edit_rate(rate_id: int, new_rate: int, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)):

    """
    The edit_rate function allows a user to edit their rating of a community.
        The function takes in the rate_id, new_rate, db and current_user as parameters.
        It then calls the edit_rate function from repository/ratings.py which edits the
        rate in the database and returns it if successful.

    :param rate_id: int: Identify the rate to be deleted
    :param new_rate: int: Set the new rate value
    :param db: Session: Access the database
    :param current_user: User: Get the user_id of the current user
    :return: The edited rate
    """
    edited_rate = await repository_ratings.edit_rate(rate_id, new_rate, db, current_user)
    if edited_rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.COMM_NOT_FOUND)
    return edited_rate


@router.delete("/delete/{rate_id}", response_model=RatingModel, dependencies=[Depends(allowed_remove_ratings)])
async def delete_rate(rate_id: int, db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_RATING)
    return deleted_rate


@router.get("/all", response_model=List[RatingModel], dependencies=[Depends(allowed_get_all_ratings)])
async def all_rates(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The all_rates function returns all the ratings in the database.


    :param db: Session: Get the database connection
    :param current_user: User: Get the current user from the database
    :return: A list of all the ratings in the database
    """
    comments = await repository_ratings.show_ratings(db, current_user)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_RATING)
    return comments


@router.get("/all_my", response_model=List[RatingModel], dependencies=[Depends(allowed_commented_by_user)])
async def all_my_rates(db: Session = Depends(get_db), current_user: User = Depends(auth_service.get_current_user)):
    """
    The all_rates function returns all the ratings in the database.


    :param db: Session: Get the database connection
    :param current_user: User: Get the current user from the database
    :return: A list of all the ratings in the database
    """
    comments = await repository_ratings.show_my_ratings(db, current_user)
    if comments is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_RATING)
    return comments


@router.get("/user_post/{user_id}/{post_id}", response_model=RatingModel,
            dependencies=[Depends(allowed_user_post_rate)])
async def user_rate_post(user_id: int, post_id: int, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
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


@router.get("/commented/{user_id}", response_model=List[PostResponse], dependencies=[Depends(allowed_commented_by_user)])
async def commented_by_user(user_id: int, db: Session = Depends(get_db),
                            current_user: User = Depends(auth_service.get_current_user)):

    """
    The commented_by_user function returns a list of posts that the user has commented on.
        The function takes in an integer representing the user_id and two optional parameters:
            - db: A database session object to be used for querying data from the database.
                If not provided, a new one will be created by calling get_db().
            - current_user: An object representing the currently logged-in user. This is obtained by calling auth_service's get_current_user() method.

    :param user_id: int: Get the user id of the user that is being searched for
    :param db: Session: Get the database session
    :param current_user: User: Get the current user and check if they are an admin
    :return: A list of posts that the user has commented on
    """
    posts = await repository_ratings.commented_by_user_posts(user_id, db, current_user)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_RATING)
    return posts


@router.get("/mine", response_model=List[PostResponse], dependencies=[Depends(allowed_commented_by_user)])
async def commented_by_me(db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)):

    """
    The commented_by_me function returns a list of posts that the current user has commented on.
        The function takes in a database session and the current_user as parameters, and returns a list of posts.

    :param db: Session: Get the database session
    :param current_user: User: Get the current user from the database
    :return: A list of posts that the user has commented on
    """
    posts = await repository_ratings.commented_by_me(db, current_user)
    if posts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_RATING)
    return posts


@router.get("/post/{post_id}", response_model=float | None, dependencies=[Depends(allowed_commented_by_user)])
async def post_rating(post_id: int, current_user: User = Depends(auth_service.get_current_user),
                      db: Session = Depends(get_db)
                      ):

    """
    The post_rating function is used to rate a post.
        The function takes in the post_id and current_user as parameters,
        and returns the rating of that particular user on that particular post.

    :param post_id: int: Get the post id from the url
    :param current_user: User: Get the user who is currently logged in
    :param db: Session: Get the database session
    :return: A rating object
    """
    rate = await repository_ratings.post_score(post_id, db, current_user)
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message.NO_RATING)
    return rate
