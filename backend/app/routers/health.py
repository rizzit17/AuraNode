from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["Health"])

@router.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.API_ENV
    }
