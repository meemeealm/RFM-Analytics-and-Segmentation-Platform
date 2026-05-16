import joblib
import glob 
import os

import warnings
warnings.filterwarnings('ignore')

files = glob.glob('rfm_pipeline_*.pkl')
latest_file = max(files, key=os.path.getctime)

model_pipe = joblib.load(latest_file)

def predict_new_customer(new_customer_data):
    return model_pipe.predict(new_customer_data)[0]
