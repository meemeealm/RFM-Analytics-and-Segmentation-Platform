import os
import glob 
import joblib
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


files = glob.glob('rfm_pipeline_*.pkl')
if not files:
    raise FileNotFoundError("No 'rfm_pipeline_*.pkl' files found in the working directory.")

latest_file = max(files, key=os.path.getctime)
model_pipe = joblib.load(latest_file)
print(f"Loaded latest model pipeline: {latest_file}")


def predict_customers(data: pd.DataFrame) -> list:
    """
    Accepts a Pandas DataFrame of customer metrics, passes it through 
    the loaded sklearn pipeline, and returns a list of cluster predictions.
    
    Expected columns (lowercase match): ['recency', 'frequency', 'monetary']
    """
    try:
        # Pass the entire matrix through the log -> scale -> kmeans pipeline
        predictions = model_pipe.predict(data)
        
        # Convert numpy array to standard Python list for FastAPI JSON compatibility
        return predictions.tolist()
        
    except Exception as e:
        raise ValueError(f"Prediction failed. Ensure feature names and types match training. Error: {e}")