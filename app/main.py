from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import ContextMiddleware

# import routers
#from app.api.v1.routers.analytics import analytics_router
from app.api.api import router as api_router_v1

app = FastAPI()


# Global context middleware configuration
middleware = [
    Middleware(
        ContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin()
        )
    )
]


@app.get('/', tags=['Welcome page'])
async def index():
    """Welcome page"""
    return {
        "User bahavior": "Analysis"
    }

# Include top-level routers
app.include_router(api_router_v1, prefix="/v1")