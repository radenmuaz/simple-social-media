from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserBase(BaseModel):
    id: int
    username: str


class CommentBase(BaseModel):
    id: int
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime


class PostBase(BaseModel):
    id: int
    image_path: Optional[str] = None
    caption: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=20)


class UserLogin(BaseModel):
    username: str
    password: str


class UserLogout(BaseModel):
    pass


class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True


class UserDeleteRequest(BaseModel):
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PostUpdate(BaseModel):
    caption: Optional[str] = Field(None, min_length=1, max_length=255)


class CommentResponse(CommentBase):
    author: UserBase

    class Config:
        orm_mode = True


class PostResponse(PostBase):
    author: UserBase
    comments: List[CommentResponse] = []

    class Config:
        orm_mode = True


class CommentCreate(BaseModel):
    post_id: int
    content: str = Field(..., min_length=1, max_length=500)


class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=500)


PostResponse.model_rebuild()
