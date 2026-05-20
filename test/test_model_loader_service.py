from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import joblib

from app.services.model_loader_service import ModelLoaderService


class DummyPipeline:
    def predict(self, _features):
        return [0]


class FakeBlob:
    def __init__(self, name: str, payload: bytes, updated: datetime):
        self.name = name
        self._payload = payload
        self.updated = updated

    def download_as_bytes(self) -> bytes:
        return self._payload


class FakeBucket:
    def __init__(self, blobs: dict[str, FakeBlob]):
        self._blobs = blobs

    def list_blobs(self, prefix: str = ""):
        return [blob for name, blob in self._blobs.items() if name.startswith(prefix)]

    def get_blob(self, name: str):
        return self._blobs.get(name)

    def blob(self, name: str):
        return self._blobs[name]


class FakeClient:
    def __init__(self, buckets: dict[str, FakeBucket]):
        self._buckets = buckets

    def bucket(self, name: str) -> FakeBucket:
        return self._buckets[name]


class FakeStorageModule:
    def __init__(self, buckets: dict[str, FakeBucket]):
        self._buckets = buckets

    def Client(self) -> FakeClient:  # noqa: N802
        return FakeClient(self._buckets)


class ModelLoaderServiceTests(unittest.TestCase):
    def tearDown(self):
        ModelLoaderService.clear_cache()

    def test_load_latest_local_model(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            older = temp_path / "rfm_pipeline_older.pkl"
            newer = temp_path / "rfm_pipeline_newer.pkl"

            joblib.dump(DummyPipeline(), older)
            joblib.dump(DummyPipeline(), newer)
            older.touch()
            newer.touch()

            model, source = ModelLoaderService.load_latest_model(
                [str(temp_path / "rfm_pipeline_*.pkl")]
            )

            self.assertEqual(str(newer), source)
            self.assertEqual([0], model.predict(None))

    def test_load_direct_gcs_model(self):
        payload = self._dump_pipeline_bytes("test_model_direct.pkl")
        blobs = {
            "models/rfm_pipeline.pkl": FakeBlob(
                name="models/rfm_pipeline.pkl",
                payload=payload,
                updated=datetime(2026, 5, 18, tzinfo=timezone.utc),
            )
        }
        storage = FakeStorageModule({"bucket-a": FakeBucket(blobs)})

        with patch.object(
            ModelLoaderService,
            "_get_storage_module",
            return_value=storage,
        ):
            model, source = ModelLoaderService.load_latest_model(
                ["gs://bucket-a/models/rfm_pipeline.pkl"]
            )

        self.assertEqual("gs://bucket-a/models/rfm_pipeline.pkl", source)
        self.assertEqual([0], model.predict(None))

    def test_load_latest_gcs_model_from_wildcard(self):
        first_payload = self._dump_pipeline_bytes("test_model_one.pkl")
        second_payload = self._dump_pipeline_bytes("test_model_two.pkl")
        blobs = {
            "models/rfm_pipeline_2026-05-17.pkl": FakeBlob(
                name="models/rfm_pipeline_2026-05-17.pkl",
                payload=first_payload,
                updated=datetime(2026, 5, 17, tzinfo=timezone.utc),
            ),
            "models/rfm_pipeline_2026-05-18.pkl": FakeBlob(
                name="models/rfm_pipeline_2026-05-18.pkl",
                payload=second_payload,
                updated=datetime(2026, 5, 18, tzinfo=timezone.utc),
            ),
        }
        storage = FakeStorageModule({"bucket-a": FakeBucket(blobs)})

        with patch.object(
            ModelLoaderService,
            "_get_storage_module",
            return_value=storage,
        ):
            model, source = ModelLoaderService.load_latest_model(
                ["gs://bucket-a/models/rfm_pipeline_*.pkl"]
            )

        self.assertEqual("gs://bucket-a/models/rfm_pipeline_2026-05-18.pkl", source)
        self.assertEqual([0], model.predict(None))

    def _dump_pipeline_bytes(self, file_name: str) -> bytes:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / file_name
            joblib.dump(DummyPipeline(), file_path)
            return file_path.read_bytes()


if __name__ == "__main__":
    unittest.main()
