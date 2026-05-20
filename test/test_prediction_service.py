import pytest
from unittest.mock import MagicMock
from app.services.prediction_service import PredictionService
from app.schemas.customer import BatchTransactionRequest 

def test_predict_batch_raw_calculation():
    mock_pipeline = MagicMock()  # This stands in for your ML model pipeline object
    dummy_source = "test_mock_source"
    
    # Initialize the service class with its required arguments
    service = PredictionService(model_pipeline=mock_pipeline, model_source=dummy_source) 
    
    # Create mock transaction objects that have a .model_dump() method
    mock_transaction_1 = MagicMock()
    mock_transaction_1.model_dump.return_value = {
        "customer_id": "12345", 
        "invoice_no": "INV-001", 
        "invoice_date": "2026-05-18", 
        "quantity": 2, 
        "unit_price": 10.0
    }
    
    mock_transaction_2 = MagicMock()
    mock_transaction_2.model_dump.return_value = {
        "customer_id": "12345", 
        "invoice_no": "INV-002", 
        "invoice_date": "2026-05-20", 
        "quantity": 4, 
        "unit_price": 5.5
    }

    # Create the mock payload matching what the function expects
    mock_payload = MagicMock(spec=BatchTransactionRequest)
    mock_payload.transactions = [mock_transaction_1, mock_transaction_2]
    
    # Run your business logic function
    result = service.predict_batch_raw(payload=mock_payload)
    
    # (Add your assertions below depending on what predict_batch_raw returns)