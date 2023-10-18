from fastapi import APIRouter
from .v1.routers import analytics
from .v1.routers import statement

router = APIRouter()

# Include API v1 routers
router.include_router(analytics.analytics_router, prefix="/analytics", tags=["analytics"])
router.include_router(statement.router, prefix="/statement", tags=["statements"])
