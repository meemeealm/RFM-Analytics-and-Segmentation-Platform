from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.ml.mappings import CLUSTER_DETAILS
from app.schemas.customer import BatchPredictRequest, CustomerPredictRequest
from app.schemas.prediction import BatchPredictionResponse, PredictionResponse
from app.services.model_loader_service import ModelLoaderService


@dataclass(slots=True)
class PredictionService:
    model_pipeline: object
    model_path: Path

    @classmethod
    def from_model_paths(cls, model_search_paths: list[str]) -> "PredictionService":
        model_pipeline, model_path = ModelLoaderService.load_latest_model(model_search_paths)
        return cls(model_pipeline=model_pipeline, model_path=model_path)

    def predict(self, payload: CustomerPredictRequest) -> PredictionResponse:
        features = pd.DataFrame(
            [
                {
                    "recency": payload.recency,
                    "frequency": payload.frequency,
                    "monetary": payload.monetary,
                }
            ]
        )
        cluster_id = int(self.model_pipeline.predict(features)[0])
        cluster_details = CLUSTER_DETAILS.get(cluster_id)

        if cluster_details is None:
            raise ValueError(f"Prediction returned unmapped cluster_id={cluster_id}.")

        return PredictionResponse(
            customerid=payload.customerid,
            cluster_id=cluster_id,
            cluster_name=str(cluster_details["cluster_name"]),
            business_summary=str(cluster_details["business_summary"]),
            recommended_actions=list(cluster_details["recommended_actions"]),
        )

    def predict_batch(self, payload: BatchPredictRequest) -> BatchPredictionResponse:
        predictions = [self.predict(customer) for customer in payload.customers]
        return BatchPredictionResponse(predictions=predictions)
