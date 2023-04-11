from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.database.models import User
from src.services.email import send_email
from src.database.connect_db import get_db
from src.schemas import UserModel, UserResponse, TokenModel, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.messages import (ALREADY_EXISTS, EMAIL_ALREADY_CONFIRMED, EMAIL_CONFIRMED,
                               EMAIL_NOT_CONFIRMED, INVALID_EMAIL, INVALID_PASSWORD, INVALID_TOKEN, SUCCESS_CREATE_USER,
                               VERIFICATION_ERROR, CHECK_YOUR_EMAIL, USER_NOT_ACTIVE, USER_IS_LOGOUT)

router = APIRouter(prefix='/auth', tags=["authentication"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
    It takes an email, username and password as input parameters.
    The function then checks if the email is already registered with another account. If it is, it returns a 409 error code (conflict).
    Otherwise, it hashes the password using bcrypt and stores both username and hashed password in the database.

    :param body: UserModel: Get the user information from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Pass the database session to the repository layer
    :return: A dict with two keys: user and detail
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=ALREADY_EXISTS)
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {"user": new_user, "detail": SUCCESS_CREATE_USER}


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.

    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Pass the database session to the function
    :return: A dict with the access_token, refresh_token and token type
    """
    user = await repository_users.get_user_by_email(body.username, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_EMAIL)
    if not user.is_verify:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=EMAIL_NOT_CONFIRMED)
    # Check is_active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=USER_NOT_ACTIVE)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_PASSWORD)
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email}, expires_delta=7200)
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Security(security),
                 db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    token = credentials.credentials

    await repository_users.add_to_blacklist(token, db)
    return {"message": USER_IS_LOGOUT}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db),
            current_user: User = Depends(auth_service.get_current_user)):
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns an access_token, a new refresh_token, and the type of token (bearer).
    
    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Pass the database session to the function
    :return: A dictionary with the access_token, refresh_token and token_type
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_TOKEN)

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes in the token that was sent to the user's email and uses it to get their email address.
        Then, it gets the user from our database using their email address and checks if they exist. If not, an error is thrown.
        Next, we check if they have already confirmed their account by checking if confirmed = True for them in our database (if so, an error is thrown).
        Finally, we set confirmed = True for them in our database.

    :param token: str: Get the token from the url
    :param db: Session: Get the database connection
    :return: A dictionary with the message &quot;email confirmed&quot;
    """

    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=VERIFICATION_ERROR)
    if user.is_verify:
        return {"message": EMAIL_ALREADY_CONFIRMED}
    await repository_users.confirmed_email(email, db)
    return {"message": EMAIL_CONFIRMED}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to verify their account. The function takes in a RequestEmail object, which contains the email of
    the user who wants to verify their account. It then checks if there is already an existing user with
    that email address and if they have already verified their account. If not, it sends them an email
    with a link that will allow them to do so.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A message that the email has been sent
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.is_verify:
        return {"message": EMAIL_CONFIRMED}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": CHECK_YOUR_EMAIL}


