from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime
import enum
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class UserRole(str, enum.Enum):
    REPORTER = "reporter"
    ENGINEER = "engineer"
    DISPATCHER = "dispatcher"
    LEADER = "leader"
    ADMIN = "admin"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    WAITING_FOR_ACCEPTANCE = "waiting_for_acceptance"
    COMPLETED = "completed"

class OrderPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"

class DispatchMethod(str, enum.Enum):
    AUTO = "auto"
    MANUAL = "manual"

class WorkOrder(SQLModel, table=True):
    __tablename__ = "work_orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: str = Field(unique=True, index=True)
    reporter_id: int = Field(foreign_key="users.id")
    description: str
    media_urls: Optional[List[str]] = Field(default=None, sa_column=Column(JSONB))
    priority: OrderPriority = OrderPriority.NORMAL
    category: str
    status: OrderStatus = OrderStatus.PENDING
    dispatch_method: DispatchMethod = DispatchMethod.AUTO
    handler_id: Optional[int] = Field(default=None, foreign_key="users.id")
    satisfaction_score: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = None

    reporter: "User" = Relationship(back_populates="work_orders")
    handler: Optional["User"] = Relationship(back_populates="handled_orders")
    records: List["ProcessRecord"] = Relationship(back_populates="work_order")

class ProcessRecord(SQLModel, table=True):
    __tablename__ = "process_records"

    id: Optional[int] = Field(default=None, primary_key=True)
    work_order_id: int = Field(foreign_key="work_orders.id")
    user_id: int = Field(foreign_key="users.id")
    action: str
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    work_order: "WorkOrder" = Relationship(back_populates="records")
    user: "User" = Relationship(back_populates="process_records")

