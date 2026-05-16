import joblib
from datetime import datetime

import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer
from sklearn.cluster import KMeans


log_transformer = FunctionTransformer(np.log1p, validate=True)

pipe = Pipeline([
    ('log', log_transformer),
    ('scaler', scaler),  # fitted scaler
    ('kmeans', kmeans)   # fitted kmeans model
])


# Create the timestamp (Format: YYYY-MM-DD)
date_str = datetime.now().strftime("%Y-%m-%d")

filename = f'rfm_pipeline_{date_str}.pkl'

# Save the pipeline
joblib.dump(pipe, filename)

print(f"Model saved as: {filename}")