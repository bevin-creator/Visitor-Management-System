# User model for authentication and role-based access control

from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class User(Base):
    __tablename__="users"

    id: Mapped[int]=mapped_column(primary_key=True, index=True)
    username: Mapped[str]=mapped_column(String(100), unique=True, index=True)
    email: Mapped[str]=mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str]=mapped_column(String(255))
    full_name: Mapped[str]=mapped_column(String(100))

    #Defining roles like admin, guard and manager
    role: Mapped[str]=mapped_column(String(20))

    #instead of deleting users, it deactivates them to preserve audit trails
    is_active: Mapped[bool]=mapped_column(Boolean, default=True)

    #timestamps
    created_at: Mapped[datetime]=mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime]= mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
