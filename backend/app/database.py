#Database connection and session management.

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# SQLite needs check_same_thread=False for FastAPI threading
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

#creates db session, pass to route and close after finish or crash
def get_db():
    db = SessionLocal()
    try:
        yield db

    finally:
        db.close()

##def my_route(db: Session = Depends(get_db)): (in FAstAPI)