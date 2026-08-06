#Visitor management routes, CRUD and search operations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.visitor import Visitor, VisitRecord
from app.schemas.visitor import VisitorCreate, VisitorResponse
from app.services.audit import log_action
from app.routers.auth import get_current_user, require_role

from app.services.encryption import encrypt_field, decrypt_field

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
    visitors = query.offset(skip).limit(limit).all()

    #decrypt
    for v in visitors:
        if v.phone:
            v.phone = decrypt_field(v.phone)
        if v.id_number:
            v.id_number = decrypt_field(v.id_number)

    return visitors

#creatin a visitor
@router.post("/", response_model=VisitorResponse, status_code=201)
async def create_visitor(
    visitor_data: VisitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    visitor = Visitor(**visitor_data.model_dump())

    #encrypt before saving
    if visitor.phone:
        visitor.phone = encrypt_field(visitor.phone)
    if visitor.id_number:
        visitor.id_number = encrypt_field(visitor.id_number)

    db.add(visitor)
    db.commit()
    db.refresh(visitor)

    if visitor.phone:
        visitor.phone = decrypt_field(visitor.phone)
    if visitor.id_number:
        visitor.id_number = decrypt_field(visitor.id_number)

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

    if visitor.phone:
        visitor.phone = decrypt_field(visitor.phone)
    if visitor.id_number:
        visitor.id_number = decrypt_field(visitor.id_number)

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

#Delete visitor (require admin role)
@router.delete("/{visitor_id}", status_code=204)
async def delete_visitor(
    visitor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),

):

    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()

    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")

    #remove all visit records for the visitor first
    db.query(VisitRecord).filter(VisitRecord.visitor_id == visitor_id).delete()
    db.delete(visitor)
    db.commit()

    #audit logging
    log_action(db, action="delete", resource_type="visitor", user_id=current_user.id, resource_id=visitor_id, details=f"Deleted visitor {visitor.full_name} and all visit records")

    return None


