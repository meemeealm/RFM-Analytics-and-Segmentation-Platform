from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    model_search_paths: list[str] = Field(
        default_factory=lambda: [
            str(Path("training") / "outputs" / "models" / "rfm_pipeline_*.pkl"),
            "rfm_pipeline_*.pkl",
            "rfm_pipeline.pkl",
        ]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
