from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.ml.mappings import CLUSTER_DETAILS
from app.schemas.customer import (
    BatchPredictRequest,
    BatchTransactionRequest,
    CustomerPredictRequest,
)
from app.schemas.prediction import BatchPredictionResponse, PredictionResponse
from app.services.model_loader_service import ModelLoaderService


@dataclass(slots=True)
class PredictionService:
    model_pipeline: object
    model_source: str

    @classmethod
    def from_model_paths(cls, model_search_paths: list[str]) -> "PredictionService":
        model_pipeline, model_source = ModelLoaderService.load_latest_model(model_search_paths)
        return cls(model_pipeline=model_pipeline, model_source=model_source)

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
            customer_id=str(payload.customer_id),
            cluster_id=cluster_id,
            cluster_name=str(cluster_details["cluster_name"]),
            business_summary=str(cluster_details["business_summary"]),
            recommended_actions=list(cluster_details["recommended_actions"]),
        )

    def predict_batch(self, payload: BatchPredictRequest) -> BatchPredictionResponse:
        predictions = [self.predict(customer) for customer in payload.customers]
        return BatchPredictionResponse(predictions=predictions)

    def predict_batch_raw(self, payload: BatchTransactionRequest) -> BatchPredictionResponse:
        raw_data = [transaction.model_dump() for transaction in payload.transactions]
        df = pd.DataFrame(raw_data)

        df["invoice_date"] = pd.to_datetime(df["invoice_date"])
        df["total_spend"] = df["quantity"] * df["unit_price"]

        latest_invoice_date = df["invoice_date"].max()
        rfm = (
            df.groupby("customer_id")
            .agg(
                recency=("invoice_date", lambda x: float((latest_invoice_date - x.max()).days)),
                frequency=("invoice_no", "nunique"),
                monetary=("total_spend", "sum"),
            )
            .reset_index()
        )

        predictions = [
            self.predict(
                CustomerPredictRequest(
                    customer_id=str(row.customer_id),
                    recency=float(row.recency),
                    frequency=float(row.frequency),
                    monetary=float(row.monetary),
                )
            )
            for row in rfm.itertuples(index=False)
        ]
        return BatchPredictionResponse(predictions=predictions)
