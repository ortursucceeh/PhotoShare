# import pickle
# from typing import Optional

# import redis
# from jose import JWTError, jwt
# from fastapi import HTTPException, status, Depends
# from fastapi.security import OAuth2PasswordBearer
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session

# from src.database.connect_db import get_db
# from src.repository import users as repository_users
# from src.conf.config import settings
# from src.conf.messages import FAIL_EMAIL_VERIFICATION, INVALID_SCOPE, NOT_VALIDATE_CREDENTIALS


# class Auth:
#     pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#     SECRET_KEY = settings.secret_key
#     ALGORITHM = settings.algorithm
#     oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

#     redis_cache = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

#     def verify_password(self, plain_password, hashed_password):
#         """
#         The verify_password function takes a plain-text password and the hashed version of that password,
#             and returns True if they match, False otherwise. This is used to verify that the user's login
#             credentials are correct.

#         :param self: Represent the instance of the class
#         :param plain_password: Store the password that is entered by the user
#         :param hashed_password: Check if the password is correct
#         :return: A boolean value
#         """
#         return self.pwd_context.verify(plain_password, hashed_password)

#     def get_password_hash(self, password: str):
#         """
#         The get_password_hash function takes a password as input and returns the hash of that password.
#             The function uses the pwd_context object to generate a hash from the given password.

#         :param self: Represent the instance of the class
#         :param password: str: Get the password from the user
#         :return: A hash of the password
#         """
#         return self.pwd_context.hash(password)

#     # define a function to generate a new access token
#     async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
#         """
#         The create_access_token function creates a new access token for the user.


#         :param self: Represent the instance of the class
#         :param data: dict: Pass the data that will be encoded in the access token
#         :param expires_delta: Optional[float]: Set the expiration time of the token
#         :return: A jwt token that is encoded with the user's information
#         """
#         to_encode = data.copy()
#         if expires_delta:
#             expire = datetime.utcnow() + timedelta(seconds=expires_delta)
#         else:
#             expire = datetime.utcnow() + timedelta(minutes=15)
#         to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
#         encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
#         return encoded_access_token

#     # define a function to generate a new refresh token
#     async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
#         """
#         The create_refresh_token function creates a refresh token for the user.
#             Args:
#                 data (dict): The data to be encoded in the JWT. This should include at least an email address and a username, but can also include other information such as first name, last name, etc.
#                 expires_delta (Optional[float]): The number of seconds until this token expires. If not provided, it will default to 7 days from now.

#         :param self: Represent the instance of the class
#         :param data: dict: Pass the data to be encoded into the jwt token
#         :param expires_delta: Optional[float]: Set the time for which the token is valid
#         :return: A refresh token in the form of a jwt
#         """
#         to_encode = data.copy()
#         if expires_delta:
#             expire = datetime.utcnow() + timedelta(seconds=expires_delta)
#         else:
#             expire = datetime.utcnow() + timedelta(days=7)
#         to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
#         encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
#         return encoded_refresh_token

#     def create_email_token(self, data: dict):
#         """
#         The create_email_token function creates a JWT token that is used to verify the user's email address.
#             The token contains the following data:
#                 - iat (issued at): The time when the token was created.
#                 - exp (expiration): When this token expires, 3 days from now.
#                 - scope: What this JWT can be used for, in this case it is an email_token which means it can only be used to verify an email address.

#         :param self: Represent the instance of the class
#         :param data: dict: Pass in the data that you want to encode
#         :return: A token
#         """
#         to_encode = data.copy()
#         expire = datetime.utcnow() + timedelta(days=3)
#         to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "email_token"})
#         token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
#         return token

#     async def decode_refresh_token(self, refresh_token: str):
#         """
#         The decode_refresh_token function takes a refresh token and decodes it.
#             If the scope is 'refresh_token', then we return the email address of the user.
#             Otherwise, we raise an HTTPException with status code 401 (UNAUTHORIZED) and detail message 'Invalid scope for token'.
#             If there was a JWTError, then we also raise an HTTPException with status code 401 (UNAUTHORIZED) and detail message 'Could not validate credentials'.

#         :param self: Represent the instance of the class
#         :param refresh_token: str: Pass the refresh token to the function
#         :return: The email of the user
#         """
#         try:
#             payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
#             if payload['scope'] == 'refresh_token':
#                 email = payload['sub']
#                 return email
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE)
#         except JWTError:
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=NOT_VALIDATE_CREDENTIALS)

#     async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#         """
#         The get_current_user function is a dependency that will be called by the FastAPI framework to retrieve the current user.
#         It uses the token provided in the Authorization header of each request and validates it against our JWT secret key.
#         If successful, it returns an instance of User with all its properties populated from our database.

#         :param self: Represent the instance of a class
#         :param token: str: Get the token from the header of a request
#         :param db: Session: Get the database session
#         :return: The user object
#         """
#         credentials_exception = HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=NOT_VALIDATE_CREDENTIALS
#         )

#         try:
#             # Decode JWT
#             payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
#             if payload['scope'] == 'access_token':
#                 email = payload["sub"]
#                 if email is None:
#                     raise credentials_exception
#             else:
#                 raise credentials_exception
#         except JWTError as e:
#             raise credentials_exception

#         user = self.redis_cache.get(f'user:{email}')
#         if user is None:
#             print("USER POSTGRES")
#             user = await repository_users.get_user_by_email(email, db)
#             if user is None:
#                 raise credentials_exception
#             self.redis_cache.set(f'user:{email}', pickle.dumps(user))
#             self.redis_cache.expire(f'user:{email}', 900)
#         else:
#             print("USER CACHE")
#             user = pickle.loads(user)
#         return user

#     async def get_email_from_token(self, token: str):
#         """
#         The get_email_from_token function takes a token as an argument and returns the email associated with that token.
#             If the scope of the token is not 'email_token', then it raises an HTTPException.
#             If there is a JWTError, then it also raises an HTTPException.

#         :param self: Represent the instance of the class
#         :param token: str: Decode the token
#         :return: A string, which is the email address of the user
#         """
#         try:
#             payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
#             if payload['scope'] == 'email_token':
#                 email = payload["sub"]
#                 return email
#             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=INVALID_SCOPE)
#         except JWTError as e:
#             print(e)
#             raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                                 detail=FAIL_EMAIL_VERIFICATION)


# auth_service = Auth()
