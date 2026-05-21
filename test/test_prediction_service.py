from unittest.mock import MagicMock

import pandas as pd

from app.schemas.customer import BatchTransactionRequest, CustomerPredictRequest
from app.schemas.prediction import BatchPredictionResponse, PredictionResponse
from app.services.prediction_service import PredictionService


def test_predict_batch_raw_calculation():
    mock_pipeline = MagicMock()
    mock_pipeline.predict.return_value = [2]
    service = PredictionService(model_pipeline=mock_pipeline, model_source="test_mock_source")

    mock_transaction_1 = MagicMock()
    mock_transaction_1.model_dump.return_value = {
        "customer_id": "12345",
        "invoice_no": "INV-001",
        "invoice_date": "2026-05-18",
        "quantity": 2,
        "unit_price": 10.0,
    }

    mock_transaction_2 = MagicMock()
    mock_transaction_2.model_dump.return_value = {
        "customer_id": "12345",
        "invoice_no": "INV-002",
        "invoice_date": "2026-05-20",
        "quantity": 4,
        "unit_price": 5.5,
    }

    mock_payload = MagicMock(spec=BatchTransactionRequest)
    mock_payload.transactions = [mock_transaction_1, mock_transaction_2]

    result = service.predict_batch_raw(payload=mock_payload)

    assert isinstance(result, BatchPredictionResponse)
    assert len(result.predictions) == 1
    assert result.predictions[0].customer_id == "12345"
    assert result.predictions[0].cluster_id == 2

    mock_pipeline.predict.assert_called_once()
    actual_df_passed = mock_pipeline.predict.call_args[0][0]
    assert isinstance(actual_df_passed, pd.DataFrame)
    assert actual_df_passed.to_dict(orient="records") == [
        {"recency": 0.0, "frequency": 2.0, "monetary": 42.0}
    ]


def test_prediction_service_logic():
    mock_pipeline = MagicMock()
    mock_pipeline.predict.return_value = [3]

    service = PredictionService(
        model_pipeline=mock_pipeline,
        model_source="gs://mock-bucket/models/rfm_pipeline_v1.pkl",
    )

    mock_payload = MagicMock(spec=CustomerPredictRequest)
    mock_payload.customer_id = 2345
    mock_payload.recency = 12.0
    mock_payload.frequency = 5
    mock_payload.monetary = 450.0

    result = service.predict(payload=mock_payload)

    assert isinstance(result, PredictionResponse)
    assert result.cluster_id == 3
    assert result.customer_id == "2345"

    mock_pipeline.predict.assert_called_once()
    actual_df_passed = mock_pipeline.predict.call_args[0][0]
    assert isinstance(actual_df_passed, pd.DataFrame)
    assert actual_df_passed.to_dict(orient="records") == [
        {"recency": 12.0, "frequency": 5, "monetary": 450.0}
    ]
