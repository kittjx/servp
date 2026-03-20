from sqlmodel import Field, SQLModel, Relationship, func
from typing import Optional, List
from datetime import datetime
import enum
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    WAITING_FOR_ACCEPTANCE = "waiting_for_acceptance"
    COMPLETED = "completed"

class OrderPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"

class DispatchMethod(str, enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(unique=True, index=True)
    reporter_id: int = Field(foreign_key="users.id", index=True)
    description: str
    media_urls: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    priority: OrderPriority = OrderPriority.NORMAL
    category: str
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    dispatch_method: DispatchMethod = DispatchMethod.AUTO
    handler_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    satisfaction_score: Optional[int] = None

    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )

    reporter: "User" = Relationship(
        back_populates="orders",
        sa_relationship_kwargs={"foreign_keys": "[Order.reporter_id]"}
    )
    handler: Optional["User"] = Relationship(
        back_populates="handled_orders",
        sa_relationship_kwargs={"foreign_keys": "[Order.handler_id]"}
    )
    records: List["ProcessRecord"] = Relationship(back_populates="order")

class ProcessRecord(SQLModel, table=True):
    __tablename__ = "process_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    user_id: int = Field(foreign_key="users.id")
    action: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    )

    order: "Order" = Relationship(back_populates="records")
    user: "User" = Relationship(back_populates="process_records")

