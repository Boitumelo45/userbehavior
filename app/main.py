from fastapi import FastAPI
from .api.v1.routers.analytics import analytics_router

router = FastAPI()


@router.get('/', tags=['Welcome page'])
async def index():
    """Welcome page"""
    return {
        "User bahavior": "Analysis"
    }

# include routers
router.include_router(analytics_router)