from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Relationship
from sqlalchemy import String

import enum

if TYPE_CHECKING:
    from .order import Order, ProcessRecord


class UserRole(str, enum.Enum):
    REPORTER = "reporter"  # 普通用户
    ENGINEER = "engineer"  # 工程师（可以接单）
    DISPATCHER = "dispatcher"  # 调度员
    LEADER = "leader"  # 部门领导
    ADMIN = "admin"  # 管理员


class User(SQLModel, table=True):
    """User model for WeChat login"""
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    openid: str = Field(index=True, unique=True, max_length=100)
    nickname: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    gender: Optional[int] = Field(default=0)  # 0: unknown, 1: male, 2: female
    phone: Optional[str] = Field(default=None, max_length=20)
    department: Optional[str] = Field(default=None, max_length=100)
    role: UserRole = Field(default=UserRole.REPORTER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    

    # Relationships
    orders: List["Order"] = Relationship(
        back_populates="reporter",
        sa_relationship_kwargs={"foreign_keys": "[Order.reporter_id]"}
    )
    handled_orders: List["Order"] = Relationship(
        back_populates="handler",
        sa_relationship_kwargs={"foreign_keys": "[Order.handler_id]"}
    )
    process_records: List["ProcessRecord"] = Relationship(back_populates="user")


class UserLoginResponse(SQLModel):
    """Response model for user login"""
    access_token: str
    token_type: str = "bearer"
    user: User


class WeChatLoginRequest(SQLModel):
    """Request model for WeChat login"""
    code: str
    user_info: Optional[dict] = None
