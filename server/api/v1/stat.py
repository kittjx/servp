
from fastapi import APIRouter
from sqlmodel import SQLModel, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import case
from typing import List, Dict

from ...db.database import DBSession
from ...models.order import WorkOrder, OrderStatus

class DashboardOverview(SQLModel):
    total_orders: int
    pending_orders: int
    processing_orders: int
    completed_orders: int

stat_router = APIRouter(prefix="/api/v1/stat")

@stat_router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(session: DBSession):
    # Single query to get all counts using conditional aggregation
    statement = select(
        func.count(WorkOrder.id),
        func.count(case((WorkOrder.status == OrderStatus.PENDING, 1))),
        func.count(case((WorkOrder.status == OrderStatus.PROCESSING, 1))),
        func.count(case((WorkOrder.status == OrderStatus.COMPLETED, 1)))
    )
    result = await session.exec(statement)
    total, pending, processing, completed = result.one()

    return DashboardOverview(
        total_orders=total,
        pending_orders=pending,
        processing_orders=processing,
        completed_orders=completed,
    )

class DashboardSummary(SQLModel):
    category: str
    status: OrderStatus
    count: int

@stat_router.get("/summary", response_model=List[DashboardSummary])
async def get_dashboard_summary(session: DBSession):
    statement = select(
        WorkOrder.category,
        WorkOrder.status,
        func.count(WorkOrder.id).label("count")
    ).group_by(WorkOrder.category, WorkOrder.status)
    
    result = await session.exec(statement)
    results = result.all()
    
    # This is already efficient, no major change needed.
    return [
        DashboardSummary(category=category, status=status, count=count)
        for category, status, count in results
    ]

class DashboardEfficiency(SQLModel):
    average_completion_time_seconds: float

@stat_router.get("/efficiency", response_model=DashboardEfficiency)
async def get_dashboard_efficiency(session: DBSession):
    # Calculate average completion time for completed orders
    statement = select(func.avg(
        func.extract("epoch", WorkOrder.completed_at) - func.extract("epoch", WorkOrder.created_at)
    )).where(WorkOrder.status == OrderStatus.COMPLETED, WorkOrder.completed_at.is_not(None))
    
    result = await session.exec(statement)
    average_completion_time = result.one_or_none()
    
    return DashboardEfficiency(
        average_completion_time_seconds=float(average_completion_time or 0)
    )

class SatisfactionStatistics(SQLModel):
    total_ratings: int
    average_score: float
    score_distribution: Dict[str, int]

@stat_router.get("/satisfaction", response_model=SatisfactionStatistics)
async def get_satisfaction_statistics(session: DBSession):
    # Single query for total ratings and average score
    stats_statement = select(
        func.count(WorkOrder.satisfaction_score),
        func.avg(WorkOrder.satisfaction_score)
    ).where(WorkOrder.satisfaction_score.is_not(None))
    
    stats_result = await session.exec(stats_statement)
    total_ratings, average_score = stats_result.one()

    # Single query for score distribution using GROUP BY
    dist_statement = select(
        WorkOrder.satisfaction_score,
        func.count(WorkOrder.id)
    ).where(WorkOrder.satisfaction_score.is_not(None)).group_by(WorkOrder.satisfaction_score)

    dist_result = await session.exec(dist_statement)
    
    # Initialize distribution with 0 for all possible scores
    score_distribution = {str(score): 0 for score in range(1, 6)}
    # Update with actual counts from the database
    for score, count in dist_result:
        if score is not None:
            score_distribution[str(score)] = count
    
    return SatisfactionStatistics(
        total_ratings=total_ratings,
        average_score=float(average_score or 0.0),
        score_distribution=score_distribution
    )
