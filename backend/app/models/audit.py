# Audit logs model

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class AuditLog(Base):
    __tablename__="audit_logs"

    id: Mapped[int]=mapped_column(primary_key=True, index=True)

    #Who
    user_id: Mapped[Optional[int]]=mapped_column(Integer, nullable=True)

    #what i.e User1 performed a checkin on visit_record4
    action: Mapped[str]=mapped_column(String(50))
    resource_type: Mapped[str]=mapped_column(String(50)) #visitor, user or visit_record
    resource_id: Mapped[Optional[int]]=mapped_column(Integer, nullable=True)

    #context
    details: Mapped[Optional[str]]=mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]]=mapped_column(String(45), nullable=True)

    #When
    timestamp: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    