#FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, visitors, checkin, reports, dashboard

from app.database import Base, engine, SessionLocal
from app import models
from app.models.user import User 
from app.routers.auth import get_password_hash

Base.metadata.create_all(bind=engine)

#create first admin from env vars
def bootstrap_admin():
    if not settings.ADMIN_USERNAME or not settings.ADMIN_PASSWORD:
        return
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            return
        admin = User(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL or "admin@example.com",
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name=settings.ADMIN_FULL_NAME,
            role="admin",
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()

bootstrap_admin()


app = FastAPI(
    title = "Visitor Management System",
    description = "API form managing visitor registration, check-in/out and reporting",
    version="1.0",
)

#CORS Conf fro frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(visitors.router, prefix="/api/v1/visitors", tags=["Visitors"])
app.include_router(checkin.router, prefix="/api/v1/checkin", tags=["Check-In/Out"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Visitor Management System API", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}