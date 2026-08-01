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
    created_at: datetime

    class Config:
        from_attributes = True


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