from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# Define a Pydantic model for input validation and data handling
class PostBase(BaseModel):
    title: str  # Title of the post (string)
    content: str  # Content of the post (string)
    published: bool = True  # Optional field with default value as True

class PostCreate(PostBase):
    pass

class Post(PostBase):
    created_at: datetime
    id: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class userOut(BaseModel):
    id:int
    email:str
    created_at: datetime

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email:EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id:Optional[str] = None








