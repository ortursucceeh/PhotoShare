from datetime import datetime
import sqlalchemy
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum

from src.database.models import UserRoleEnum


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=25)
    avatar: Optional[str]


class UserDb(BaseModel):
    id: int
    username: str = Field(min_length=5, max_length=25)
    email: str
    avatar: Optional[str]
    role: UserRoleEnum
    created_at: datetime

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# Hashtag
class HashtagBase(BaseModel):
    title: str = Field(max_length=25)
    
    
class HashtagModel(HashtagBase):
    pass
    

class HashtagResponse(HashtagBase):
    id: int
    # user: UserDb
    user_id: int
    created_at: datetime
    
    class Config:
        orm_mode = True
        
        
# Comment
# class CommentBase(BaseModel):
#     text: str = Field(max_length=500)
    
    
# class CommentModel(CommentBase):
#     pass
    
    
# class CommentUpdate(CommentModel):
#     done = bool
    
    
# class CommentResponse(CommentModel):
#     id: int
#     created_at: datetime
#     updated_at = datetime
    
#     class Config:
#         orm_mode = True
        

# # Rating
# class RatingBase(BaseModel):
#     rate: float
    
    
# class RatingModel(RatingBase):
#     pass
    
    
# class RatingUpdate(RatingModel):
#     done = bool
    
    
# class RatingResponse(RatingModel):
#     id: int
#     created_at: datetime
#     updated_at = datetime
    
#     class Config:
#         orm_mode = True


# Post
class PostBase(BaseModel):
    image_url: str = Field(max_length=300)
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    hashtags: Optional[List[HashtagBase]] = None
    # rating: float = None

    @validator("hashtags")
    def validate_tags(cls, v):
        if len(v or []) > 5:
            raise ValueError("Too many hashtags. Maximum 5 tags allowed.")
        return v


class PostModel(PostBase):
    hashtags: List[str]


class PostUpdate(PostModel):
    done: bool 
    updated_at: datetime
    hashtags: List[str]
    
class PostResponse(PostBase):
    id: int
    hashtags: List[HashtagResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# class RequestEmail(BaseModel):
#     email: EmailStr
