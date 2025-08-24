from pydantic import BaseModel, EmailStr
from typing import Optional, List

# === Auth ===
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    roles: List[str] = []

    class Config:
        from_attributes = True

class LoginIn(BaseModel):
    username: str
    password: str

# === Blog Posts ===
class PostCreate(BaseModel):
    title: str
    content: str
    is_public: bool = True

class PostOut(BaseModel):
    id: int
    title: str
    content: str
    is_public: bool
    author_id: int

    class Config:
        from_attributes = True

# === Discussions & Messages ===
class DiscussionCreate(BaseModel):
    title: str

class MessageCreate(BaseModel):
    discussion_id: int
    body: str

# === Status ===
class StatusCreate(BaseModel):
    text: str
