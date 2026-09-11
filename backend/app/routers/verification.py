#id verification route
#endpoint running the verification service

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.visitor import Visitor
from app.routers.auth import get_current_user
from app.schemas.visitor import VerifyIdRequest, VerifyIdResponse
from app.services import id_verification
from app.services.audit import log_action
from app.services.encryption import decrypt_field

router = APIRouter()


#verify an id, either an existing visitor by id or raw details passed in
@router.post("/verify-id", response_model=VerifyIdResponse)
async def verify_id(
    payload: VerifyIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    id_type = payload.id_type
    id_number = payload.id_number
    full_name = payload.full_name
    visitor = None

    #if a visitor id is given, pull their details, decrypting the stored id number
    if payload.visitor_id is not None:
        visitor = db.query(Visitor).filter(Visitor.id == payload.visitor_id).first()
        if not visitor:
            raise HTTPException(status_code=404, detail="Visitor not found")
        id_type = id_type or visitor.id_type
        id_number = id_number or decrypt_field(visitor.id_number)
        full_name = full_name or visitor.full_name

    #run the check, this returns not_configured when the api var isnt set
    result = id_verification.verify_id(
        id_type=id_type,
        id_number=id_number,
        full_name=full_name,
    )

    #if it was tied to a visitor, save the latest status back on them
    if visitor is not None:
        visitor.verification_status = result["status"]
        visitor.verification_checked_at = datetime.utcnow()
        db.commit()

        #auditlogging via audit service
        log_action(db, action="verify", resource_type="visitor", user_id=current_user.id, resource_id=visitor.id, details=f"ID verification for {visitor.full_name}: {result['status']}")

    return {
        "status": result["status"],
        "provider": result["provider"],
        "detail": result["detail"],
        "checked_at": result["checked_at"],
        "visitor_id": payload.visitor_id,
    }


#quick check of whether the verification api is wired up yet
@router.get("/status")
async def verification_status(
    current_user: User = Depends(get_current_user),
):
    return {"configured": id_verification.is_configured()}
