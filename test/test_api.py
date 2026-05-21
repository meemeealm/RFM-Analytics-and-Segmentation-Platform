from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app


def test_predict_batch_raw_endpoint() -> None:
    mock_service = MagicMock()
    mock_service.predict_batch_raw.return_value = {
        "predictions": [
            {
                "customer_id": "12345",
                "cluster_id": 2,
                "cluster_name": "High-Value",
                "business_summary": "Top spending customer",
                "recommended_actions": ["Offer loyalty perks"],
            }
        ]
    }

    payload = {
        "transactions": [
            {
                "customer_id": "12345",
                "invoiceno": "INV-001",
                "stockcode": "SKU-001",
                "description": "Sample item",
                "quantity": 2,
                "invoicedate": "2026-05-20T00:00:00",
                "unitprice": 10.0,
                "country": "Singapore",
                "status": "completed",
            }
        ]
    }

    with patch("app.main.create_prediction_service", return_value=mock_service):
        with TestClient(app) as client:
            response = client.post("/api/v1/customers/predict/batch/raw", json=payload)

    assert response.status_code == 200, response.text
    assert response.json() == {
        "predictions": [
            {
                "customer_id": "12345",
                "cluster_id": 2,
                "cluster_name": "High-Value",
                "business_summary": "Top spending customer",
                "recommended_actions": ["Offer loyalty perks"],
            }
        ]
    }
    mock_service.predict_batch_raw.assert_called_once()
