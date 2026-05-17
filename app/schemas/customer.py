from pydantic import BaseModel, Field


class CustomerPredictRequest(BaseModel):
    customerid: str = Field(..., min_length=1, description="External customer identifier")
    recency: float = Field(..., ge=0, description="Days since the most recent purchase")
    frequency: float = Field(..., ge=0, description="Number of distinct purchases")
    monetary: float = Field(..., ge=0, description="Total customer spend")


class BatchPredictRequest(BaseModel):
    customers: list[CustomerPredictRequest] = Field(
        ..., min_length=1, description="Customers to score in a single request"
    )
