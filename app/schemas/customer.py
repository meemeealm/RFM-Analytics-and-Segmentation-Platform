from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class CustomerPredictRequest(BaseModel):
    customer_id: str = Field(..., min_length=1, description="External customer identifier")
    recency: float = Field(..., description="Days since the most recent purchase")
    frequency: float = Field(..., description="Number of distinct purchases")
    monetary: float = Field(..., description="Total customer spend")

    @field_validator("recency", "frequency", "monetary", mode="before")
    @classmethod
    def validate_rfm_numeric_input(cls, value: Any, info) -> Any:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{info.field_name} must be a numeric value.")
        return value

    @field_validator("recency", "frequency", "monetary")
    @classmethod
    def validate_rfm_non_negative(cls, value: float, info) -> float:
        if value < 0:
            raise ValueError(f"{info.field_name} must be non-negative.")
        return value


class BatchPredictRequest(BaseModel):
    customers: list[CustomerPredictRequest] = Field(
        ..., min_length=1, description="Customers to score in a single request"
    )


class RawTransaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    invoice_no: str = Field(..., alias="invoiceno")
    stock_code: str = Field(..., alias="stockcode")
    description: str | None = None
    quantity: int
    invoice_date: str = Field(..., alias="invoicedate")
    unit_price: float = Field(..., alias="unitprice")
    customer_id: str = Field(
        ...,
        alias="customer_id",
        validation_alias=AliasChoices("customer_id", "customerid"),
    )
    country: str | None = None
    status: str

class BatchTransactionRequest(BaseModel):
    transactions: list[RawTransaction] = Field(
        ..., min_length=1, description="Raw customer transactions to aggregate into RFM features"
    )
