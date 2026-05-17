from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.clusters import router as clusters_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.services.prediction_service import PredictionService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.prediction_service = PredictionService.from_model_paths(
        model_search_paths=settings.model_search_paths
    )
    yield


app = FastAPI(
    title="Customer Intelligence Orchestrator",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(customers_router, prefix="/api/v1")
app.include_router(clusters_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
