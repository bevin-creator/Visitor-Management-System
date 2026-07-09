# Check-in and check-out routes

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.visitor import VisitRecord
from app.routers.auth import get_current_user
from app.schemas.visitor import CheckInRequest, CheckOutRequest, VisitRecordResponse

router = APIRouter()

#check-in
@router.post("/", response_model=VisitRecordResponse, status_code=201)
async def check_in_visitor(
    checkin_data: CheckInRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Create a new visit record
    visit_record = VisitRecord(
        visitor_id=checkin_data.visitor_id,
        purpose=checkin_data.purpose,
        host_name=checkin_data.host_name,
        host_department=checkin_data.host_department,
        badge_number=checkin_data.badge_number,
        notes=checkin_data.notes,
        checked_in_by=current_user.id,
    )
    db.add(visit_record)
    db.commit()
    db.refresh(visit_record)
    return visit_record


#check-out
@router.post("/checkout", response_model=VisitRecordResponse)
async def check_out_visitor(
    checkout_data: CheckOutRequest,
    db: Session=Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    visit_record=(
        db.query(VisitRecord)
        .filter(VisitRecord.id==checkout_data.visit_record_id)
        .first()
    )
    if not visit_record:
        raise HTTPException(status_code=404, detail="visit record not found")
    if visit_record.check_out_time:
        raise HTTPException(status_code=400, detail="visitor already checked out")

    visit_record.check_out_time= datetime.utcnow()
    visit_record.checked_out_by=current_user.id
    if checkout_data.notes:
        visit_record.notes=checkout_data.notes

    db.commit()
    db.refresh(visit_record)
    return visit_record


#list active visitors
@router.get("/active", response_model=list[VisitRecordResponse])
async def get_active_visits(
    db: Session=Depends(get_db),
    current_user: User=Depends(get_current_user),
):
    return(
        db.query(VisitRecord)
        .filter(VisitRecord.check_out_time.is_(None))
        .order_by(VisitRecord.check_in_time.desc())
        .all()
    )
