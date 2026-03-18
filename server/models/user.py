from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String


class User(SQLModel, table=True):
    """User model for WeChat login"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(index=True, unique=True, max_length=100)
    nickname: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    gender: Optional[int] = Field(default=0)  # 0: unknown, 1: male, 2: female
    city: Optional[str] = Field(default=None, max_length=50)
    province: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=50)
    language: Optional[str] = Field(default=None, max_length=20)
    phone: Optional[str] = Field(default=None, max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserLoginResponse(SQLModel):
    """Response model for user login"""
    access_token: str
    token_type: str = "bearer"
    user: User


class WeChatLoginRequest(SQLModel):
    """Request model for WeChat login"""
    code: str
    user_info: Optional[dict] = None
