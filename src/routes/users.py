from typing import List

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from src.database.connect_db import get_db
from src.repository import users as repository_users
from src.database.models import User, UserRoleEnum
from src.schemas import PostResponse, UserProfileModel, UserResponseModel, RequestEmail, UserDb, RequestRole
from src.services.auth import auth_service
from src.services.roles import RoleChecker
from src.conf.messages import NOT_FOUND, USER_ROLE_EXISTS, INVALID_EMAIL, USER_NOT_ACTIVE, USER_ALREADY_NOT_ACTIVE,\
    USER_CHANGE_ROLE_TO

router = APIRouter(prefix='/users', tags=["users"])

allowed_get_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_create_user = RoleChecker([UserRoleEnum.admin, UserRoleEnum.moder, UserRoleEnum.user])
allowed_get_all_users = RoleChecker([UserRoleEnum.admin])
allowed_remove_user = RoleChecker([UserRoleEnum.admin])
allowed_ban_user = RoleChecker([UserRoleEnum.admin])
allowed_change_user_role = RoleChecker([UserRoleEnum.admin])


@router.get("/me/", response_model=UserDb)
async def read_my_profile(current_user: User = Depends(auth_service.get_current_user),
                        db: Session = Depends(get_db)):
    """
    The read_my_profile function returns the current user's profile information.
    
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: An object of type user
    """
    user = await repository_users.get_me(current_user, db)
    return user


@router.put("/edit_me/", response_model=UserDb)
async def edit_my_profile(avatar: UploadFile = File(), new_username: str = Form(None),
                          current_user: User = Depends(auth_service.get_current_user), db: Session = Depends(get_db)):
    """
    The edit_my_profile function allows a user to edit their profile.
        The function takes in an avatar, new_username and current_user as parameters.
        It returns the updated user.
    
    :param avatar: UploadFile: Upload a new avatar to the user's profile
    :param new_username: str: Update the username of a user
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the repository layer
    :return: The updated user
    """
    updated_user = await repository_users.edit_my_profile(avatar, new_username, current_user, db)
    return updated_user

    
@router.get("/all", response_model=List[UserDb], dependencies=[Depends(allowed_get_all_users)])
async def read_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    The read_all_users function returns a list of users.
        ---
        get:
          summary: Returns all users.
          description: This can only be done by the logged in user.
          operationId: read_all_users
          parameters:
            - name: skip (optional)  # The number of records to skip before returning results, default is 0 (no records skipped).  Used for pagination purposes.   See https://docs.mongodb.com/manual/reference/method/cursor.skip/#cursor-skip-examples for more information on how this
    
    :param skip: int: Skip the first n records
    :param limit: int: Limit the number of results returned
    :param db: Session: Pass the database connection to the function
    :return: A list of users
    """
    users = await repository_users.get_users(skip, limit, db)
    return users


@router.get("/users_with_username/{username}", response_model=List[UserResponseModel],
            dependencies=[Depends(allowed_get_user)])
async def read_users_by_username(username: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_users_by_username function is used to read users by username.
        It returns a list of users with the given username.
    
    :param username: str: Specify the username of the user we want to retrieve
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user
    :return: A list of users with the given username
    """
    users = await repository_users.get_users_with_username(username, db)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return users


@router.get("/user_profile_with_username/{username}", response_model=UserProfileModel,
            dependencies=[Depends(allowed_get_user)])
async def read_user_profile_by_username(username: str, db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_user_profile_by_username function is used to read a user profile by username.
        The function takes in the username as an argument and returns the user profile if it exists.
    
    :param username: str: Get the username from the url path
    :param db: Session: Pass the database session to the repository layer
    :param current_user: User: Get the current user's information
    :return: A userprofile object
    """
    user_profile = await repository_users.get_user_profile(username, db)
    if user_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return user_profile


@router.get("/commented_posts_by_me/", response_model=List[PostResponse])
async def read_commented_posts_by_me(db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_commented_posts_by_me function returns all posts that the current user has commented on.
    
    :param db: Session: Get the database session
    :param current_user: User: Get the user that is currently logged in
    :return: A list of posts that the user has commented on
    """
    posts = await repository_users.get_all_commented_posts(current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.get("/rated_posts_by_me/", response_model=List[PostResponse])
async def read_liked_posts_by_me(db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_liked_posts_by_me function returns all posts liked by the current user.
        The function is called when a GET request is made to the /users/me/liked_posts endpoint.
    
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user object of the current logged in user
    :return: A list of posts that the user liked
    """
    posts = await repository_users.get_all_liked_posts(current_user, db)
    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return posts


@router.patch("/ban/{email}/", dependencies=[Depends(allowed_ban_user)])
async def ban_user_by_email(body: RequestEmail, db: Session = Depends(get_db)):
    """
    The ban_user_by_email function takes a user's email address and bans the user from accessing the API.
        If the email is not found in our database, an HTTPException is raised with status code 401 (Unauthorized) and
        detail message &quot;Invalid Email&quot;. If the user has already been banned, an HTTPException is raised with status code 409
        (Conflict) and detail message &quot;User Already Not Active&quot;. Otherwise, if no exceptions are thrown, we return a JSON object
        containing key-value pair {&quot;message&quot;: USER_NOT_ACTIVE}.
    
    :param body: RequestEmail: Get the email from the request body
    :param db: Session: Get the database session
    :return: A dictionary with a message
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if user.is_active:
        await repository_users.ban_user(user.email, db)
        return {"message": USER_NOT_ACTIVE}
    else:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=USER_ALREADY_NOT_ACTIVE)


@router.patch("/make_role/{email}/", dependencies=[Depends(allowed_change_user_role)])
async def make_role_by_email(body: RequestRole, db: Session = Depends(get_db)):
    """
    The make_role_by_email function is used to change the role of a user.
        The function takes in an email and a role, and changes the user's role to that specified by the inputted
        parameters. If no such user exists, then an HTTPException is raised with status code 401 (Unauthorized)
        and detail message &quot;Invalid Email&quot;. If the new role matches that of the current one, then a message saying so
        will be returned. Otherwise, if all goes well, then a success message will be returned.
    
    :param body: RequestRole: Get the email and role from the request body
    :param db: Session: Access the database
    :return: A dictionary with a message key
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if body.role == user.role:
        return {"message": USER_ROLE_EXISTS}
    else:
        await repository_users.make_user_role(body.email, body.role, db)
        return {"message": f"{USER_CHANGE_ROLE_TO} {body.role.value}"}


