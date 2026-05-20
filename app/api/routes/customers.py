from fastapi import APIRouter, Depends, Request

from app.core.security import require_api_key_placeholder
from app.schemas.customer import BatchPredictRequest, BatchTransactionRequest, CustomerPredictRequest
from app.schemas.prediction import BatchPredictionResponse, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(
    prefix="/customers",
    tags=["customers"],
    dependencies=[Depends(require_api_key_placeholder)],
)


def get_prediction_service(request: Request) -> PredictionService:
    return request.app.state.prediction_service


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Predict a customer's segment from RFM metrics",
)
async def predict_customer(
    payload: CustomerPredictRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> PredictionResponse:
    return prediction_service.predict(payload)


@router.post(
    "/predict/batch",
    response_model=BatchPredictionResponse,
    summary="Predict customer segments in batch from RFM metrics",
)
async def predict_customers_batch(
    payload: BatchPredictRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> BatchPredictionResponse:
    return prediction_service.predict_batch(payload)


@router.post(
    "/predict/batch/raw",
    response_model=BatchPredictionResponse,
    summary="Predict customer segments from raw transaction logs",
)
async def predict_customers_batch_raw(
    payload: BatchTransactionRequest,
    prediction_service: PredictionService = Depends(get_prediction_service),
) -> BatchPredictionResponse:
    return prediction_service.predict_batch_raw(payload)




