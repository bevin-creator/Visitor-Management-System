#FastAPI

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, visitors, checkin, reports, dashboard

from app.database import Base, engine
from app import models  

Base.metadata.create_all(bind=engine)

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