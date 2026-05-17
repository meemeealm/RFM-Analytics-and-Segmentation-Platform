from __future__ import annotations

from glob import glob
from pathlib import Path
from typing import Any

import joblib


class ModelLoaderService:
    @staticmethod
    def load_latest_model(model_search_paths: list[str]) -> tuple[Any, Path]:
        candidates: list[Path] = []

        for pattern in model_search_paths:
            candidates.extend(Path(path) for path in glob(pattern))

        if not candidates:
            raise FileNotFoundError(
                "No trained pipeline artifact was found. Checked configured model search paths."
            )

        latest_model_path = max(candidates, key=lambda path: path.stat().st_mtime)
        return joblib.load(latest_model_path), latest_model_path

