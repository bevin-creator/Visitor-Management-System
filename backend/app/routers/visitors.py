#Visitor management routes, CRUD and search operations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.visitor import Visitor
from app.routers.auth import get_current_user
from app.schemas.visitor import VisitorCreate, VisitorResponse
from app.services.audit import log_action


router = APIRouter()

#listing visitors + search capability
@router.get("/", response_model=list[VisitorResponse])
async def list_visitors(
    search: Optional[str] = Query(None, description="Search by name, email or phone"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Visitor)

    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            Visitor.full_name.ilike(search_filter)
            | Visitor.email.ilike(search_filter)
            | Visitor.phone.ilike(search_filter)
        )

    return query.offset(skip).limit(limit).all()

#creatin a visitor
@router.post("/", response_model=VisitorResponse, status_code=201)
async def create_visitor(
    visitor_data: VisitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = Visitor(**visitor_data.model_dump())
    db.add(visitor)
    db.commit()
    db.refresh(visitor)

    #auditlogging via audit service
    log_action(db, action="create", resource_type="visitor", user_id=current_user.id, resource_id=visitor.id, details=f"Registered visitor {visitor.full_name}")


    return visitor


#Read one visitor by ID
@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(
    visitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


#Updating visitor record
@router.put("/{visitor_id}", response_model=VisitorResponse)
async def update_visitor(
    visitor_id: int,
    visitor_data: VisitorCreate,
    db: Session= Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()

    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    for key, value in visitor_data.model_dump().items():
        setattr(visitor, key, value)

    db.commit()
    db.refresh(visitor)
    return visitor



