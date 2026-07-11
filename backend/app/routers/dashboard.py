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
    current_user: User = Depends(get_current_user),
):

    today=datetime.utcnow().date()
    start_of_today=datetime.combine(today, datetime.min.time())
    start_of_week=start_of_today - timedelta(days=today.weekday())

    visitors_today=(
        db.query(func.count(VisitRecord.id))
        .filter(VisitRecord.check_in_time >= start_of_today)
        .scalar()
    )

    currently_checked_in=(
        db.query(func.count(VisitRecord.id))
        .filter(VisitRecord.check_out_time == None)
        .scalar()
    )
    visitors_this_week=(
        db.query(func.count(VisitRecord.id))
        .filter(VisitRecord.check_in_time >= start_of_week)
        .scalar()   
    )

    return{
        "visitors_today": visitors_today,
        "currently_checked_in": currently_checked_in,
        "visitors_this_week": visitors_this_week,
    }


#recent visitors endpoint
@router.get("/recent")
async def get_recent_visitors(
    limit: int=10,
    db: Session=Depends(get_db),
    current_user: User=Depends(get_current_user),
):

    return(
        db.query(VisitRecord)
        .order_by(VisitRecord.check_in_time.desc())
        .limit(limit)
        .all()
    )