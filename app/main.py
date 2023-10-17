from fastapi import FastAPI
from .routers.analytics import analytics_router

router = FastAPI()


@router.get('/', tags=['Welcome page'])
async def index():
    """Welcome page"""
    return {
        "User bahavior": "Analysis"
    }

# include routers
router.include_router(analytics_router)