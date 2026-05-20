from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.clusters import router as clusters_router
from app.api.routes.customers import router as customers_router
from app.api.routes.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.middleware.request_logger import RequestLoggingMiddleware
from app.services.model_loader_service import ModelLoaderService
from app.services.prediction_service import PredictionService


def create_prediction_service() -> PredictionService:
    settings = get_settings()
    return PredictionService.from_model_paths(model_search_paths=settings.model_search_paths)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.prediction_service = create_prediction_service()
    yield
    ModelLoaderService.clear_cache()


app = FastAPI(
    title="Customer Intelligence Prediction",
    version="0.1.0",
    lifespan=lifespan,
)

configure_logging()
app.add_middleware(RequestLoggingMiddleware)

app.include_router(customers_router, prefix="/api/v1")
app.include_router(clusters_router, prefix="/api/v1")
app.include_router(health_router, prefix="/api/v1")
