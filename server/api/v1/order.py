from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...db.database import DBSession
from ...models.order import WorkOrder, OrderStatus, OrderPriority, ProcessRecord, DispatchMethod

from typing import List, Optional
from datetime import datetime
import random
import string

def generate_order_id():
    now = datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{date_str}-{random_str}"

class WorkOrderCreate(SQLModel):
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
    work_order_id: int
    action: str
    notes: Optional[str] = None

class ReassignOrderRequest(SQLModel):
    order_id: int
    new_handler_id: int


order_router = APIRouter(prefix="/api/v1/order")

async def get_work_order_or_404(order_id: int, session: AsyncSession) -> WorkOrder:
    """Helper to fetch a WorkOrder by its ID or raise a 404 error."""
    result = await session.exec(select(WorkOrder).where(WorkOrder.id == order_id))
    work_order = result.one_or_none()
    if not work_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="WorkOrder not found")
    return work_order

@order_router.post("/create", response_model=WorkOrder, status_code=status.HTTP_201_CREATED)
async def create_order(order: WorkOrderCreate, session: DBSession):
    work_order = WorkOrder(
        order_id=generate_order_id(),
        reporter_id=order.reporter_id,
        description=order.description,
        media_urls=order.media_urls,
        priority=order.priority,
        category=order.category
    )
    session.add(work_order)
    await session.commit()
    await session.refresh(work_order)
    return work_order

@order_router.post("/accept", response_model=WorkOrder)
async def accept_order(request: AcceptOrderRequest, session: DBSession):
    work_order = await get_work_order_or_404(request.order_id, session)
    work_order.handler_id = request.user_id
    work_order.status = OrderStatus.PROCESSING
    work_order.updated_at = datetime.utcnow()
    
    session.add(work_order)
    await session.commit()
    await session.refresh(work_order)
    return work_order

@order_router.get("/list", response_model=List[WorkOrder])
async def list_orders(
    session: DBSession,
    status: Optional[OrderStatus] = None,
    skip: int = 0,
    limit: int = 100    
):
    statement = select(WorkOrder)
    if status:
        statement = statement.where(WorkOrder.status == status)
    
    result = await session.exec(statement.offset(skip).limit(limit))
    work_orders = result.all()
    return work_orders

@order_router.post("/process", response_model=WorkOrder)
async def process_order(request: ProcessOrderRequest, session: DBSession):
    work_order = await get_work_order_or_404(request.order_id, session)
    work_order.status = OrderStatus.WAITING_FOR_ACCEPTANCE
    work_order.updated_at = datetime.utcnow()
    
    session.add(work_order)
    await session.commit()
    await session.refresh(work_order)
    return work_order

@order_router.get("/process-records/{orderId}", response_model=List[ProcessRecord])
async def get_process_records(orderId: int, session: DBSession):
    work_order = await get_work_order_or_404(orderId, session)
    return work_order.records

@order_router.post("/confirm", response_model=WorkOrder)
async def confirm_order(request: ConfirmOrderRequest, session: DBSession):
    work_order = await get_work_order_or_404(request.order_id, session)
    work_order.status = OrderStatus.COMPLETED
    work_order.completed_at = datetime.utcnow()
    work_order.updated_at = datetime.utcnow()
    if request.satisfaction_score is not None:
        work_order.satisfaction_score = request.satisfaction_score
    
    session.add(work_order)
    await session.commit()
    await session.refresh(work_order)
    return work_order

@order_router.get("/{order_id}", response_model=WorkOrder)
async def get_order_detail(order_id: int, session: DBSession):
    return await get_work_order_or_404(order_id, session)


@order_router.post("/process-record", response_model=ProcessRecord, status_code=status.HTTP_201_CREATED)
async def create_process_record(record: ProcessRecordCreate, session: DBSession):
    work_order = await get_work_order_or_404(record.work_order_id, session)
    
    process_record = ProcessRecord(
        work_order_id=record.work_order_id,
        user_id=work_order.handler_id,
        action=record.action,
        notes=record.notes
    )
    session.add(process_record)
    await session.commit()
    await session.refresh(process_record)
    return process_record


@order_router.patch("/reassign", response_model=WorkOrder)
async def reassign_order(request: ReassignOrderRequest, session: DBSession):
    work_order = await get_work_order_or_404(request.order_id, session)
    work_order.handler_id = request.new_handler_id
    work_order.dispatch_method = DispatchMethod.MANUAL
    work_order.updated_at = datetime.utcnow()
    
    session.add(work_order)
    await session.commit()
    await session.refresh(work_order)
    return work_order
