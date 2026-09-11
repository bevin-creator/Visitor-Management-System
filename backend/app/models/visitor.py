#Visitor and visit records

from datetime import datetime
from typing import Optional #Optional accomodate null

from sqlalchemy import String, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

class Visitor(Base):
    __tablename__="visitors"

    id: Mapped[int]= mapped_column(primary_key=True, index=True)
    full_name: Mapped[str]=mapped_column(String(100), index=True)
    email: Mapped[str]= mapped_column(String(100), nullable=True, index=True)
    phone: Mapped[str]=mapped_column(String(20))
    phone_bidx: Mapped[Optional[str]]=mapped_column(String(64), nullable=True, index=True)
    company: Mapped[Optional[str]]=mapped_column(String(100), nullable=True)
    id_type: Mapped[Optional[str]]=mapped_column(String(50), nullable=True)
    id_number: Mapped[Optional[str]]=mapped_column(String(50), nullable=True)
    id_number_bidx: Mapped[Optional[str]]=mapped_column(String(64), nullable=True, index=True)

    #timespamps and r/ship
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    visits: Mapped[list["VisitRecord"]]=relationship(back_populates="visitor")


    #visit records
class VisitRecord(Base):
    __tablename__="visit_records"

    id: Mapped[int]= mapped_column(primary_key=True, index=True)
    visitor_id: Mapped[int]=mapped_column(ForeignKey("visitors.id"), index=True)

    #visit details
    purpose: Mapped[str]= mapped_column(String(50))
    host_name: Mapped[str]=mapped_column(String(100))
    host_department: Mapped[Optional[str]]=mapped_column(String(100), nullable=True)
    badge_number: Mapped[Optional[str]]=mapped_column(String(20), nullable=True)

    #check-in/out time
    check_in_time: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    check_out_time: Mapped[Optional[datetime]]=mapped_column(DateTime, nullable=True)

    #Notes & audit fields
    notes: Mapped[Optional[str]]=mapped_column(Text, nullable=True)
    checked_in_by: Mapped[Optional[int]]=mapped_column(ForeignKey("users.id"), nullable=True)
    checked_out_by: Mapped[Optional[int]]=mapped_column(ForeignKey("users.id"), nullable=True)

    visitor: Mapped["Visitor"]=relationship(back_populates="visits")

