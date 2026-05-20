import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _get_model_search_paths() -> list[str]:
    configured_paths = os.getenv("MODEL_SEARCH_PATHS")
    search_paths: list[str] = []

    if configured_paths:
        search_paths.extend(path.strip() for path in configured_paths.split(",") if path.strip())

    model_gcs_uri = os.getenv("MODEL_GCS_URI")
    if model_gcs_uri:
        search_paths.append(model_gcs_uri)

    if search_paths:
        return search_paths

    project_root = _project_root()
    return [
        str(project_root / "training" / "outputs" / "models" / "rfm_pipeline_*.pkl"),
        str(project_root / "rfm_pipeline_*.pkl"),
        str(project_root / "rfm_pipeline.pkl"),
    ]


class Settings(BaseModel):
    api_key: str | None = Field(
        default_factory=lambda: os.getenv("APP_API_KEY"),
        description="Optional API key used by the placeholder auth dependency.",
    )
    model_search_paths: list[str] = Field(
        default_factory=_get_model_search_paths,
        description="Ordered local or gs:// model locations. MODEL_GCS_URI is appended automatically.",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
