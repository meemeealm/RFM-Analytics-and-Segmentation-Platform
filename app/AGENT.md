You are a senior backend engineer and ML systems architect.

Build a production-ready FastAPI backend for a personal ML project called "Customer Intelligence Orchestrator".

# System Overview

The backend serves customer segmentation predictions using a pre-trained KMeans clustering model based on RFM metrics:

* Recency
* Frequency
* Monetary

The model is already trained.

The backend is inference-only.

The API will later:

* run in Docker
* deploy to Google Cloud Run
* connect to a Streamlit frontend
* download ML artifacts from Google Cloud Storage (GCS)

# Core Requirements

The backend MUST:

* load ML artifacts only once during application startup
* cache models in memory
* reuse cached models for all predictions
* NEVER download models per request
* NEVER retrain models inside the API

# Architecture Requirements

Use clean architecture with strong separation of concerns.

Project structure:

app/
├── main.py
├── api/
│   └── routes/
│       ├── health.py
│       ├── customers.py
│       └── clusters.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── exceptions.py
│   └── logging.py
│
├── services/
│   ├── prediction_service.py
│   ├── model_loader_service.py
│   ├── gcs_service.py
│   └── cluster_service.py
│
├── schemas/
│   ├── customer.py
│   ├── prediction.py
│   ├── cluster.py
│   └── response.py
│
├── ml/
│   ├── mappings.py
│   └── inference.py
│
├── middleware/
│   └── request_logger.py
│
├── utils/
│
├── tests/
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env

# Tech Stack

* FastAPI
* Pydantic v2
* scikit-learn
* pandas
* numpy
* joblib
* google-cloud-storage
* uvicorn
* uv (for env)

# ML Artifacts

The following artifacts exist in Google Cloud Storage:

* rfm_pipeline_*.pkl

Artifacts should be downloaded during startup and loaded into RAM.

Use:

* Google Cloud Storage client
* joblib.load()

# IMPORTANT STARTUP REQUIREMENT

Use FastAPI lifespan context manager.

DO NOT use:
@app.on_event("startup")

Use:
FastAPI(lifespan=lifespan)

During startup:

1. connect to GCS
2. download model artifacts
3. load artifacts into memory
4. cache them globally via app.state or singleton service

All prediction requests must use the cached in-memory model.

# Cluster Definitions

Cluster 1:

* High value
* High engagement
* VIP customers

Cluster 0:

* Recent but low buyers
* Potential growth customers

Cluster 2:

* Stable buyers
* Consistent purchasers

Cluster 3:

* At-risk low-value buyers
* Possible churn candidates

# Business Recommendation Mapping

Cluster 1:

* VIP rewards
* referral campaigns
* exclusive access

Cluster 0:

* onboarding campaigns
* first-purchase incentives
* engagement nudges

Cluster 2:

* cross-sell opportunities
* retention campaigns
* personalized bundles

Cluster 3:

* win-back campaigns
* churn prevention discounts
* reactivation emails

# API Requirements

Base URL:
/api/v1

# Endpoints

## Health Check

GET /health

Response:
{
"status": "healthy"
}

# Predict Customer Cluster

POST /customers/predict

Input:
{
"customerid": "1001",
"recency": 12,
"frequency": 8,
"monetary": 4200
}

Behavior:

* validate payload
* use cached scaler
* scale RFM features
* predict using cached KMeans model
* map cluster to business meaning
* return business insights

Example response:
{
"customerid": "1001",
"cluster_id": 1,
"cluster_name": "High Value & Highly Engaged",
"business_summary": "This customer belongs to the highest-value segment.",
"recommended_actions": [
"Offer VIP rewards",
"Launch referral campaigns"
]
}

# Batch Prediction

POST /customers/predict/batch

Accept multiple customer records.

# Cluster Metadata

GET /clusters

Return:

* cluster_id
* cluster_name
* description
* marketing recommendations

# Schema Requirements

Generate Pydantic schemas for:

* CustomerPredictRequest
* BatchPredictRequest
* PredictionResponse
* ClusterMetadata
* APIResponse

# Validation Rules

* recency >= 0
* frequency >= 0
* monetary >= 0

Return business-friendly validation messages.

# Services

## prediction_service.py

Responsible for:

* scaling
* inference
* cluster mapping
* prediction orchestration

## model_loader_service.py

Responsible for:

* downloading artifacts from GCS
* loading models
* caching models in memory

## gcs_service.py

Responsible for:

* Google Cloud Storage communication
* blob downloads
* bucket operations

## cluster_service.py

Responsible for:

* cluster metadata
* business summaries
* recommendation mappings

# Middleware

Implement:

* request logging middleware
* execution timing middleware

# Security

Add:

* CORS middleware
* API key auth placeholder

# Error Handling

Implement:

* global exception handlers
* model loading exceptions
* invalid prediction exceptions
* GCS connectivity exceptions

Convert technical failures into business-readable API responses.

# Deployment Requirements

Generate:

* Dockerfile
* docker-compose.yml
* requirements.txt
* .env.example

The API must run correctly on Cloud Run.

Use:
PORT environment variable.

# Documentation

Enable:

* Swagger docs
* endpoint descriptions
* response models

# Testing

Generate:

* pytest tests
* prediction service tests
* API integration tests

# Coding Standards

* production-ready architecture
* modular design
* type hints everywhere
* async endpoints
* clean service separation
* scalable patterns
* no monolithic files

# Important Constraints

DO NOT:

* retrain model
* download model on every request
* load model repeatedly
* place business logic directly in routes

DO:

* load once during startup
* cache model in memory
* separate services from routes
* keep ML inference centralized

Generate complete runnable code.
