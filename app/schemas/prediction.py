from pydantic import BaseModel


class PredictionResponse(BaseModel):
    customer_id: str
    cluster_id: int
    cluster_name: str
    business_summary: str
    recommended_actions: list[str]


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]
