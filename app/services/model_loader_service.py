from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from glob import glob
from io import BytesIO
from pathlib import Path
from threading import Lock
from typing import Any
from urllib.parse import urlparse

import joblib


@dataclass(frozen=True, slots=True)
class ModelCandidate:
    source: str
    updated_at: float


class ModelLoaderService:
    _cache_lock = Lock()
    _cached_model: Any | None = None
    _cached_model_source: str | None = None

    @classmethod
    def load_latest_model(cls, model_search_paths: list[str]) -> tuple[Any, str]:
        with cls._cache_lock:
            if cls._cached_model is not None and cls._cached_model_source is not None:
                return cls._cached_model, cls._cached_model_source

            model, model_source = cls._load_latest_model(model_search_paths)
            cls._cached_model = model
            cls._cached_model_source = model_source
            return model, model_source

    @staticmethod
    def _load_latest_model(model_search_paths: list[str]) -> tuple[Any, str]:
        candidates: list[ModelCandidate] = []

        for pattern in model_search_paths:
            if pattern.startswith("gs://"):
                candidates.extend(ModelLoaderService._get_gcs_candidates(pattern))
                continue

            candidates.extend(ModelLoaderService._get_local_candidates(pattern))

        if not candidates:
            raise FileNotFoundError(
                "No trained pipeline artifact was found. Checked configured model search paths. "
                "In containers, set MODEL_GCS_URI or MODEL_SEARCH_PATHS to a reachable gs:// or local path."
            )

        latest_model = max(candidates, key=lambda candidate: candidate.updated_at)
        return ModelLoaderService._load_candidate(latest_model), latest_model.source

    @staticmethod
    def _get_local_candidates(pattern: str) -> list[ModelCandidate]:
        return [
            ModelCandidate(source=str(path), updated_at=path.stat().st_mtime)
            for path in (Path(path_string) for path_string in glob(pattern))
            if path.is_file()
        ]

    @staticmethod
    def _get_gcs_candidates(pattern: str) -> list[ModelCandidate]:
        storage = ModelLoaderService._get_storage_module()
        bucket_name, object_pattern = ModelLoaderService._split_gcs_uri(pattern)
        client = storage.Client()
        bucket = client.bucket(bucket_name)

        if ModelLoaderService._has_glob_magic(object_pattern):
            prefix = ModelLoaderService._get_gcs_prefix(object_pattern)
            blobs = bucket.list_blobs(prefix=prefix)
            return [
                ModelCandidate(
                    source=f"gs://{bucket_name}/{blob.name}",
                    updated_at=blob.updated.timestamp(),
                )
                for blob in blobs
                if blob.updated is not None and fnmatch(blob.name, object_pattern)
            ]

        blob = bucket.get_blob(object_pattern)
        if blob is None or blob.updated is None:
            return []

        return [
            ModelCandidate(
                source=f"gs://{bucket_name}/{blob.name}",
                updated_at=blob.updated.timestamp(),
            )
        ]

    @staticmethod
    def _load_candidate(candidate: ModelCandidate) -> Any:
        if candidate.source.startswith("gs://"):
            storage = ModelLoaderService._get_storage_module()
            bucket_name, object_name = ModelLoaderService._split_gcs_uri(candidate.source)
            blob = storage.Client().bucket(bucket_name).blob(object_name)
            return joblib.load(BytesIO(blob.download_as_bytes()))

        return joblib.load(candidate.source)

    @staticmethod
    def _get_storage_module():
        try:
            from google.cloud import storage
        except ImportError as exc:
            raise RuntimeError(
                "google-cloud-storage is required to load models from GCS."
            ) from exc

        return storage

    @staticmethod
    def _split_gcs_uri(uri: str) -> tuple[str, str]:
        parsed = urlparse(uri)
        if parsed.scheme != "gs" or not parsed.netloc or not parsed.path.lstrip("/"):
            raise ValueError(f"Invalid GCS URI: {uri}")

        return parsed.netloc, parsed.path.lstrip("/")

    @staticmethod
    def _has_glob_magic(value: str) -> bool:
        return any(char in value for char in "*?[")

    @staticmethod
    def _get_gcs_prefix(object_pattern: str) -> str:
        wildcard_indexes = [
            index
            for wildcard in ("*", "?", "[")
            if (index := object_pattern.find(wildcard)) != -1
        ]
        first_wildcard = min(wildcard_indexes)
        prefix = object_pattern[:first_wildcard]
        slash_index = prefix.rfind("/")
        if slash_index == -1:
            return ""
        return prefix[: slash_index + 1]

    @classmethod
    def clear_cache(cls) -> None:
        with cls._cache_lock:
            cls._cached_model = None
            cls._cached_model_source = None
