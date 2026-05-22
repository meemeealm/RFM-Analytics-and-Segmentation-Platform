import streamlit as st
import pandas as pd
import requests

import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from the .env file
load_dotenv()

# Retrieve the hidden variable, providing a safe local fallback if it's missing
BASE_API_URL = os.getenv("CLOUDRUN_API_URL", "http://localhost:8080")

BATCH_API_URL = f"{BASE_API_URL}/predict/batch"
INDIVIDUAL_API_URL = f"{BASE_API_URL}/predict"

# ===================================================================

st.set_page_config(page_title="Customer Segmentation Portal", layout="wide")
st.title("📊 Customer RFM Segmentation Dashboard")

# Individual
# ===========================================

st.subheader("🎯 Single Customer Prediction Entry")
st.markdown("Manually input an individual customer's details to calculate their behavioral cluster classification instantly.")

# 2. Input Form Layout (Using columns to keep the UI clean)
with st.form(key="individual_prediction_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        customer_id = st.text_input("Customer ID", value="12345")
        recency = st.number_input(
            "Recency (Days since last purchase)", 
            min_value=0.0, 
            value=14.0, 
            step=1.0,
            help="How many days ago did this customer make their last purchase?"
        )
        
    with col2:
        frequency = st.number_input(
            "Frequency (Total number of distinct invoices)", 
            min_value=1.0, 
            value=5.0, 
            step=1.0,
            help="Total number of completed transactions across their entire account lifecycle."
        )
        monetary = st.number_input(
            "Monetary Value ($ Total Spend)", 
            min_value=0.0, 
            value=350.50, 
            step=5.0,
            help="The net financial value this customer has spent in your store."
        )
        
    # Submit Button within the form
    submit_button = st.form_submit_button(label="🚀 Analyze Customer Segment", type="primary")

# 3. Request Trigger Logic
if submit_button:
    # Build the exact JSON structure your CustomerPredictRequest Pydantic schema expects
    payload = {
        "customer_id": str(customer_id),
        "recency": float(recency),
        "frequency": float(frequency),
        "monetary": float(monetary)
    }
    
    # endpoint route (e.g., /predict or /predict/single)
    INDIVIDUAL_API_URL = "https://customer-segmentation-api-571415030807.us-central1.run.app/api/v1/customers/predict"
    
    with st.spinner("Streaming metrics to inference engine..."):
        try:
            response = requests.post(INDIVIDUAL_API_URL, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Success Announcement
                st.success(f"🎉 Analysis Complete for Customer **{result.get('customer_id')}**")
                
                # Display Metrics and Details via Clean UI Containers
                st.metric(
                    label="Assigned Segment Classification", 
                    value=result.get("cluster_name").upper()
                )
                
                with st.expander("📌 View Strategic Insights & Actions", expanded=True):
                    st.markdown(f"**Business Executive Summary:**\n{result.get('business_summary')}")
                    st.markdown("---")
                    st.markdown("**💡 Recommended Growth & Retention Actions:**")
                    for action in result.get("recommended_actions", []):
                        st.markdown(f"- {action}")
            else:
                st.error(f"Backend Engine Error ({response.status_code})")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"Failed to complete network connection: {str(e)}")

# ================================================================
# Batch
# ================================================================


# Let the user choose what kind of CSV they are uploading
data_type = st.radio(
    "Select your uploaded file data structure:",
    ("Pre-calculated RFM Metrics", "Raw Transaction History Log")
)

uploaded_file = st.file_uploader("Choose a Customer CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("📋 Uploaded Data Preview")
    st.dataframe(df.head(5), use_container_width=True)
    
    if st.button("🚀 Run Segmentation Engine", type="primary"):
        with st.spinner("Parsing data matrix to JSON schema and sending to cloud..."):
            try:
                # --- STRATEGY 1: Handling Pre-calculated RFM ---
                if data_type == "Pre-calculated RFM Metrics":
                    # Map dataframe rows into a dictionary matching BatchPredictRequest (List[CustomerData])
                    payload = {
                        "customers": df.to_dict(orient="records")
                    }
                
                # --- STRATEGY 2: Handling Raw Transactions ---
                else:
                    # Map dataframe rows into a dictionary matching BatchTransactionRequest (List[TransactionData])
                    payload = {
                        "transactions": df.to_dict(orient="records")
                    }
                
                # Fire the structured JSON payload straight to Cloud Run
                response = requests.post(BATCH_API_URL, json=payload, timeout=60)
                
                if response.status_code == 200:
                    st.success("🎉 Clusters generated successfully!")
                    
                    # Parse your structural BatchPredictionResponse object
                    response_data = response.json()
                    predictions_list = response_data.get("predictions", [])
                    
                    # Convert response back to a dataframe for display and download
                    result_df = pd.DataFrame(predictions_list)
                    
                    st.subheader("🎯 Assigned Customer Segment Results")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Download link
                    st.download_button(
                        label="📥 Download Results CSV",
                        data=result_df.to_csv(index=False).encode('utf-8'),
                        file_name="segmented_output.csv",
                        mime="text/csv"
                    )
                else:
                    st.error(f"Backend Server Error ({response.status_code})")
                    st.code(response.text)
                    
            except Exception as e:
                st.error(f"An unexpected exception occurred: {str(e)}")