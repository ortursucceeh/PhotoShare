from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, validator

from src.database.models import UserRoleEnum


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    password: str = Field(min_length=6, max_length=25)
    avatar: Optional[str]


class UserUpdateModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    
    
class UserProfileModel(BaseModel):
    username: str = Field(min_length=5, max_length=25)
    email: EmailStr
    avatar: Optional[str]
    post_count: Optional[int]
    comment_count: Optional[int]
    rates_count: Optional[int]
    is_active: Optional[bool]
    created_at: datetime
    
    
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


class HashtagBase(BaseModel):
    title: str = Field(max_length=50)


class HashtagModel(HashtagBase):
    pass

    class Config:
            orm_mode = True


class HashtagResponse(HashtagBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


# Comments
class CommentBase(BaseModel):
    text: str = Field(max_length=500)


class CommentModel(CommentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int
    post_id: int
    update_status: bool = False

    class Config:
        orm_mode = True


class CommentUpdate(CommentModel):
    update_status: bool = True
    updated_at = datetime

    class Config:
        orm_mode = True


# Rating
class RatingBase(BaseModel):
    rate: int


class RatingModel(RatingBase):
    id: int
    created_at: datetime
    post_id: int
    user_id: int

    class Config:
        orm_mode = True


# Post
class PostBase(BaseModel):
    id: int
    image_url: str = Field(max_length=300, default=None)
    transform_url: str = Field(max_length=300, default=None)
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    hashtags: List[str] = []

    @validator("hashtags")
    def validate_tags(cls, v):
        if len(v or []) > 5:
            raise ValueError("Too many hashtags. Maximum 5 tags allowed.")
        return v


class PostModel(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str = Field(max_length=45)
    descr: str = Field(max_length=450)
    hashtags: List[str] = []
    

class PostResponse(PostBase):
    hashtags: List[HashtagModel]
    avg_rating: Optional[float] = 0.0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class RequestEmail(BaseModel):
    email: EmailStr


class RequestRole(BaseModel):
    email: EmailStr
    role: UserRoleEnum
