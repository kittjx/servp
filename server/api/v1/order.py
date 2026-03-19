from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import SQLModel, select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from ...db.database import DBSession
from ...models.order import Order, OrderStatus, OrderPriority, ProcessRecord, DispatchMethod

from typing import List, Optional
from datetime import datetime
import random
import string

def generate_order_id():
    now = datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{date_str}-{random_str}"

class OrderCreate(SQLModel):
    reporter_id: int
    description: str
    media_urls: Optional[List[str]] = None
    priority: OrderPriority
    category: str

class AcceptOrderRequest(SQLModel):
    order_id: int
    user_id: int

class ProcessOrderRequest(SQLModel):
    order_id: int

class ConfirmOrderRequest(SQLModel):
    order_id: int
    satisfaction_score: Optional[int] = None

class ProcessRecordCreate(SQLModel):
    order_id: int
    action: str
    notes: Optional[str] = None

class ReassignOrderRequest(SQLModel):
    order_id: int
    new_handler_id: int


order_router = APIRouter(prefix="/api/v1/order")

async def get_order_or_404(order_id: int, session: AsyncSession) -> Order:
    """Helper to fetch an Order by its ID or raise a 404 error."""
    result = await session.exec(select(Order).where(Order.id == order_id))
    order = result.one_or_none()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order

@order_router.post("/create", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, session: DBSession):
    new_order = Order(
        order_id=generate_order_id(),
        reporter_id=order.reporter_id,
        description=order.description,
        media_urls=order.media_urls,
        priority=order.priority,
        category=order.category
    )
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)
    return new_order

@order_router.post("/accept", response_model=Order)
async def accept_order(request: AcceptOrderRequest, session: DBSession):
    order = await get_order_or_404(request.order_id, session)
    order.handler_id = request.user_id
    order.status = OrderStatus.PROCESSING
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

@order_router.get("/list", response_model=List[Order])
async def list_orders(
    session: DBSession,
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 100    
):
    statement = select(Order)
    if status:
        statement = statement.where(Order.status == status)
    
    result = await session.exec(statement.offset(skip).limit(limit))
    orders = result.all()
    return orders

@order_router.post("/process", response_model=Order)
async def process_order(request: ProcessOrderRequest, session: DBSession):
    order = await get_order_or_404(request.order_id, session)
    order.status = OrderStatus.WAITING_FOR_ACCEPTANCE
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

@order_router.get("/process-records/{orderId}", response_model=List[ProcessRecord])
async def get_process_records(orderId: int, session: DBSession):
    order = await get_order_or_404(orderId, session)
    return order.records

@order_router.post("/confirm", response_model=Order)
async def confirm_order(request: ConfirmOrderRequest, session: DBSession):
    order = await get_order_or_404(request.order_id, session)
    order.status = OrderStatus.COMPLETED
    order.completed_at = datetime.utcnow()
    order.updated_at = datetime.utcnow()
    if request.satisfaction_score is not None:
        order.satisfaction_score = request.satisfaction_score
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

@order_router.get("/{order_id}", response_model=Order)
async def get_order_detail(order_id: int, session: DBSession):
    return await get_order_or_404(order_id, session)


@order_router.post("/process-record", response_model=ProcessRecord, status_code=status.HTTP_201_CREATED)
async def create_process_record(record: ProcessRecordCreate, session: DBSession):
    order = await get_order_or_404(record.order_id, session)
    
    process_record = ProcessRecord(
        order_id=record.order_id,
        user_id=order.handler_id,
        action=record.action,
        notes=record.notes
    )
    session.add(process_record)
    await session.commit()
    await session.refresh(process_record)
    return process_record


@order_router.patch("/reassign", response_model=Order)
async def reassign_order(request: ReassignOrderRequest, session: DBSession):
    order = await get_order_or_404(request.order_id, session)
    order.handler_id = request.new_handler_id
    order.dispatch_method = DispatchMethod.MANUAL
    order.updated_at = datetime.utcnow()
    
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order
