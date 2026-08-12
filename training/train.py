import joblib
from datetime import datetime

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.cluster import KMeans


#===============
# Preparation
#===============

df = pd.read_excel("Online Retail.xlsx")
df.rename(
    columns=lambda column: "customer_id" if column.lower() == "customerid" else column.lower(),
    inplace=True,
)
df['date']= pd.to_datetime(df['invoicedate'])
df = df.dropna(subset=['customer_id'])

df_rec = df.groupby('customer_id')['date'].max().reset_index()

df['total_spend'] = df['quantity']*df['unitprice']

# calculate the ref data (latest date in the data)
latest_date = df_rec['date'].max()

# calculate days since that date
df_rec['recency'] = (latest_date - df_rec['date']).dt.days


# ============
#  Aggregation
# ============

# 1. THE AGGREGATION (Ensuring unique trips)

rfm = df.groupby('customer_id').agg({
    'invoicedate': lambda x: (latest_date - x.max()).days, # Recency
    'invoiceno': 'nunique',                               # Frequency (Unique trips!)
    'total_spend': 'sum'                                  # Monetary
}).rename(columns={'invoicedate': 'recency', 'invoiceno': 'frequency', 'total_spend': 'monetary'})

monetary_cutoff = rfm['monetary'].quantile(0.95)
rfm = rfm[(rfm['monetary'] > 0) & (rfm['monetary'] <= monetary_cutoff)]


# ===============
#  Model Preparation
# ===============

rfm_log = np.log1p(rfm[['recency', 'frequency', 'monetary']])


scaler = StandardScaler()
rfm_scaled_array = scaler.fit_transform(rfm_log)

rfm_scaled_final = pd.DataFrame(rfm_scaled_array, 
                                index=rfm.index, 
                                columns=['recency', 'frequency', 'monetary'])


rfm_scaled_final.dropna(inplace=True)


kmeans = KMeans(n_clusters=4, n_init=10, random_state=42)

rfm['Cluster'] = kmeans.fit_predict(rfm_scaled_final)


#===========
#  Model
#===========

log_transformer = FunctionTransformer(np.log1p, validate=True)

pipe = Pipeline([
    ('log', log_transformer),
    ('scaler', scaler),  # fitted scaler
    ('kmeans', kmeans)   # fitted kmeans model
])



# ========
# Save Model 
# ========

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_DIR = BASE_DIR / "outputs" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

date_str = datetime.now().strftime("%Y-%m-%d")

filename = f'rfm_pipeline_{date_str}.pkl'

MODEL_PATH = MODEL_DIR / filename


# save model
joblib.dump(pipe, MODEL_PATH)

print(f"Model saved at: {MODEL_PATH}")



# =========================
# MLflow Tracking
# =========================

import mlflow
import mlflow.sklearn
from sklearn.metrics import silhouette_score

mlflow.set_experiment("customer-segmentation")

with mlflow.start_run():

    # Metrics
    silhouette = silhouette_score(
        rfm_scaled_final,
        rfm['Cluster']
    )

    # Parameters
    mlflow.log_param("n_clusters", kmeans.n_clusters)
    mlflow.log_param("random_state", kmeans.random_state)

    # Metrics
    mlflow.log_metric("silhouette_score", silhouette)
    mlflow.log_metric("inertia", kmeans.inertia_)

    # Log full pipeline
    mlflow.sklearn.log_model(
        sk_model=pipe,
        name="rfm-pipeline"
    )

    print("MLflow tracking completed.")
