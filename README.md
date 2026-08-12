# RFM Analytics & Segmentation Platform

An end-to-end machine learning and data engineering solution designed to perform Recency, Frequency, and Monetary (RFM) customer segmentation. The system ingests data from a relational database, processes analytics in Google Cloud Platform (GCP), serves prediction models via FastAPI on Cloud Run, and provides an interactive Streamlit UI for ad-hoc user interactions.

---

### Problem Description

In modern e-commerce and retail environments, business teams often struggle to effectively segment their customer base to run personalized marketing campaigns, improve retention, and optimize customer lifetime value (LTV). Specifically, organizations face several key operational and technical challenges:

1. **Siloed Data Sources**: Transactional data sits trapped in operational databases (like MySQL) without an automated pipeline to consolidate and structure it for analytics.
2. **Lack of Automated Customer Scoring**: Calculating Recency, Frequency, and Monetary (RFM) metrics manually or through static spreadsheets is slow, prone to human error, and unable to scale as customer transaction volumes grow.
3. **Decoupled Machine Learning Workflows**: Data science teams may train customer segmentation models locally, but business users lack a simple, automated way to run predictions against live data or custom datasets.
4. **Poor Accessibility for Non-Technical Users**: Marketing and strategy teams often depend on data engineers to pull ad-hoc reports, creating operational bottlenecks when testing short-term campaigns using custom `.csv` lists.

---

## How This Platform Solves the Problem

This architecture provides a scalable, cloud-native platform that automates the end-to-end flow from raw transactional data to actionable customer segments.

* **Airflow ETL Pipelines**: Automatically pull transactional updates from operational databases (MySQL) and ingest them into **Google BigQuery**, ensuring analytical data is always fresh without impacting database performance.

* **FastAPI on Cloud Run**: Encapsulates RFM scoring logic into a lightweight, auto-scaling microservice. The service fetches feature data directly from BigQuery and loads the machine learning model (`rfm.pkl`) stored in **Google Cloud Storage (GCS)** to execute real-time scoring.

* **Streamlit**: Users can upload ad-hoc `.csv` files for immediate, on-demand scoring without needing technical support.

---

## Architecture Overview

```
+--------------------+        +----------------------------------------------------+        +---------------+
| Front-end (Ad-hoc) |        |               Google Cloud Platform                |        |  Data Source  |
|                    |        |                                                    |        |               |
|  [ Data / CSV ]    |        |   +--------------------+     +-----------------+   |        |  [ MySQL ]    |
|         |          |        |   | Infra & Backend    |     | Storage         |   |        |      |        |
|         v          |        |   |                    |     |                 |   |        |      |        |
|   [ Streamlit ] ---+--HTTPS-+-->| [ FastAPI ] <------+---->| [ BigQuery ] <--+---+Airflow-+------+        |
|         ^          |        |   | (Cloud Run)        |     |                 |   |        |               |
|         |          |        |   +---------+----------+     +--------+--------+   |        +---------------+
|         +----------+--------+-------------+                     |        |       |
|   Return Results   |        |             |                     v        v       |
|                    |        |    Artifact Registry     GCS Scores  GCS Model |
+--------------------+        +----------------------------------------------------+

```

### Data & Execution Flow

1. **ETL & Data Pipelines**:
* Customer transaction data is extracted from **MySQL** and ingested into **Google BigQuery** using **Apache Airflow**.


2. **Backend & Model Serving**:
* **FastAPI** is containerized, deployed to **Artifact Registry**, and hosted on **Google Cloud Run**.
* The API executes queries against **BigQuery** to prepare feature inputs.
* Model artifacts (`rfm.pkl`) are loaded directly from **Google Cloud Storage (GCS)** to score customer segments.
* Calculated scores are saved back to Cloud Storage (`gs: bucket/data/rfm_scores.csv`) as the final data store.


3. **Frontend Presentation**:
* A **Streamlit** dashboard provides an ad-hoc interface for users to upload custom CSV datasets or request RFM metrics via HTTPS endpoints.
* Results and segment metrics are returned from the FastAPI service and displayed visually to the end user.



---

## Tech Stack

* **Frontend**: Streamlit
* **Backend API**: FastAPI, Python
* **Data Warehouse**: Google BigQuery
* **Object Storage**: Google Cloud Storage (GCS)
* **Containerization & Deployment**: Docker, GCP Artifact Registry, GCP Cloud Run
* **Orchestration**: Airflow
* **Database**: MySQL

---

## Project Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entrypoint
│   │   ├── services/            # BigQuery and GCS integration logic
│   │   └── models/              # RFM calculation and scoring logic
│   ├── Dockerfile               # Container build file for FastAPI
│   └── requirements.txt
├── frontend/
│   ├── app.py                   # Streamlit UI interface
│   └── requirements.txt
├── airflow/
│   └── dags/                    # Airflow ETL pipelines (MySQL -> BigQuery)
├── models/
│   └── rfm.pkl                  # Model artifact for GCS upload
└── README.md

```

---

## Prerequisites

* Python 3.9+
* Docker
* Google Cloud SDK (`gcloud` CLI)
* GCP Account with permissions for BigQuery, Cloud Storage, Cloud Run, and Artifact Registry

---

## Getting Started

### 1. Environment Configuration

Create a `.env` file in the root directory with your GCP credentials and configuration details:

```env
GCP_PROJECT_ID=your-gcp-project-id
GCS_BUCKET_NAME=your-bucket-name
BIGQUERY_DATASET=your_dataset
BIGQUERY_TABLE=your_table
API_URL=https://your-cloud-run-service-url.run.app

```

### 2. Running Locally

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

```

#### Frontend Setup

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py

```

---

## Deployment Guide

### Deploying Backend to Cloud Run

1. **Build and push the Docker image to Artifact Registry**:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rfm-backend:latest ./backend

```


2. **Deploy image to Cloud Run**:
```bash
gcloud run deploy rfm-backend-service \
  --image gcr.io/YOUR_PROJECT_ID/rfm-backend:latest \
  --platform managed \
  --region us-central1

```



### Storage Setup

Ensure the required directory paths exist in your Cloud Storage bucket:

* `gs://<your-bucket>/data/rfm_scores.csv`
* `gs://<your-bucket>/model/rfm.pkl`

---

## Usage

1. Open the Streamlit web application interface.
2. Select whether to run segmentation directly against BigQuery data or upload an ad-hoc `.csv` file.
3. Submit the request to trigger the FastAPI prediction backend.
4. View generated RFM scores, segment visualizations, and download processed outputs directly from the UI.