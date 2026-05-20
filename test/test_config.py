from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from app.core.config import _get_model_search_paths, _project_root


class ConfigTests(unittest.TestCase):
    def test_default_model_paths_are_rooted_to_project(self):
        with patch.dict(os.environ, {}, clear=True):
            paths = _get_model_search_paths()

        project_root = _project_root()
        expected_paths = [
            str(project_root / "training" / "outputs" / "models" / "rfm_pipeline_*.pkl"),
            str(project_root / "rfm_pipeline_*.pkl"),
            str(project_root / "rfm_pipeline.pkl"),
        ]
        self.assertEqual(expected_paths, paths)

    def test_model_search_paths_env_takes_precedence(self):
        with patch.dict(
            os.environ,
            {
                "MODEL_SEARCH_PATHS": "gs://bucket/models/*.pkl, /models/fallback.pkl ",
                "MODEL_GCS_URI": "gs://bucket/default.pkl",
            },
            clear=True,
        ):
            paths = _get_model_search_paths()

        self.assertEqual(
            ["gs://bucket/models/*.pkl", "/models/fallback.pkl", "gs://bucket/default.pkl"],
            paths,
        )

    def test_project_root_is_repository_root(self):
        project_root = _project_root()
        self.assertTrue((project_root / "pyproject.toml").exists())
        self.assertEqual(Path("customer-segmentation"), Path(project_root.name))


if __name__ == "__main__":
    unittest.main()
