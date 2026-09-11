#defining pydantic schemas for vivitors management.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

class VisitorCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    company: Optional[str] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None

class VisitorResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    company: Optional[str]= None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    #id verification status, not_configured until the api is set up
    verification_status: Optional[str] = None
    verification_checked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


#request/response for the verify-id endpoint
class VerifyIdRequest(BaseModel):
    #verify an existing visitor by id, or pass raw details directly
    visitor_id: Optional[int] = None
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    full_name: Optional[str] = None


class VerifyIdResponse(BaseModel):
    status: str
    provider: Optional[str] = None
    detail: str
    checked_at: str
    visitor_id: Optional[int] = None


class VisitRecordCreate(BaseModel):
    visitor_id: int
    purpose: str
    host_name: str
    host_department: Optional[str]= None
    badge_number: Optional[str]= None
    notes: Optional[str]= None


class VisitRecordResponse(BaseModel):
    id: int
    visitor_id: int
    purpose: str
    host_name: str
    host_department: Optional[str]= None
    badge_number: Optional[str]= None
    check_in_time: datetime
    check_out_time: Optional[datetime]= None
    notes: Optional[str]= None

    class Config:
        from_attributes = True


class CheckInRequest(BaseModel):
    visitor_id: int
    purpose: str
    host_name: str
    host_department: Optional[str]= None
    badge_number: Optional[str]= None
    notes: Optional[str]= None


class CheckOutRequest(BaseModel):
    visit_record_id: int
    notes: Optional[str]=None

class VisitRecordWithVisitor(BaseModel):
    id: int
    visitor_id: int
    purpose: str
    host_name: str
    host_department: Optional[str]=None
    badge_number: Optional[str]=None
    check_in_time: datetime
    check_out_time: Optional[datetime]=None
    notes: Optional[str]=None
    visitor_name: str
    visitor_email: str
    visitor_phone: str
    visitor_id_type: Optional[str]=None
    visitor_id_number: Optional[str]=None

    class Config:
        from_attributes=True