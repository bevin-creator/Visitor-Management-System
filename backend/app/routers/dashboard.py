#frontend dashboard route

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.visitor import VisitRecord
from app.routers.auth import get_current_user

router = APIRouter()

#metrics endpoint
@router.get("/metrics")
async def get_dashboard_metrics(
    db: Session=Depends(get_db),
    current_user= User = Depends(get_current_user),
):

    today=datetime.utcnow().date()
    start_of_today=datetime.combine(today, datetime.min.time())
    start_of_week=start_of_today - timedelta(days=today.weekday())

    visitors_today=(
        db.query(func.count(VisitRecord,id))
        .filter(VisitRecord.chek_in_time >= start_of_today)
        .scalar()
    )
