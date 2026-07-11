#Report genration for admins and supervisors
from datetime import date, datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.visitor import Visitor, VisitRecord
from app.routers.auth import get_current_user, require_role

router = APIRouter()

#report for a range of dates
@router.get("/summary")
async def get_summary_report(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "manager")),

):
    start = datetime.combine(start_date, datetime.min.time())
    end = datetime.combine(end_date, datetime.max.time())

    total_visits =(
        db.query(func.count(VisitRecord.id))
        .filter(VisitRecord.check_in_time.between(start, end))
        .scalar()
    )

    unique_visitors = (
        db.query(func.count(func.distinct(VisitRecord.visitor_id)))
        .filter(VisitRecord.check_in_time.between(start, end))
        .scalar()
    )


    purpose_breakdown = (
        db.query(VisitRecord.purpose, func.count(VisitRecord.id))
        .filter(VisitRecord.check_in_time.between(start, end))
        .group_by(VisitRecord.purpose)
        .all()
    )

    return{
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_visits": total_visits,
        "unique_visitors": unique_visitors,
        "purpose_breakdown": {purpose: count for purpose, count in purpose_breakdown}
    }


#history for specific visitor
@router.get("/visitor/{visitor_id}/history")
async def get_visitor_history(
    visitor_id: int,
    db: Session = Depends(get_db),
    current_user: User=Depends(get_current_user),

):


    visits = (
        db.query(VisitRecord)
        .filter(VisitRecord.visitor_id == visitor_id)
        .order_by(VisitRecord.check_in_time.desc())
        .all()
        
    )
    return visits