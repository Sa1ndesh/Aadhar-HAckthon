from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .data_loader import load_all_data
from .analytics import calculate_state_growth, detect_anomalies, predict_future
import pandas as pd
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global data store (in-memory for this hackathon/demo)
DATA_STORE = {}

@app.on_event("startup")
async def startup_event():
    global DATA_STORE
    print("Loading data on startup...")
    DATA_STORE = load_all_data()
    print("Data loaded successfully.")

@app.get("/api/trends")
def get_trends():
    """
    Returns aggregated trends for Enrolment, Biometric, and Demographic updates.
    """
    response = {}
    for key, df in DATA_STORE.items():
        if not df.empty:
            trends = calculate_state_growth(df)
            # Convert to dict for JSON response
            # We'll aggregate by date for the main chart
            daily = trends.groupby('date')['total'].sum().reset_index()
            response[key] = {
                "dates": daily['date'].dt.strftime('%Y-%m-%d').tolist(),
                "values": daily['total'].tolist()
            }
    return response

@app.get("/api/anomalies")
def get_anomalies():
    """
    Returns anomalies detected in enrolment data.
    """
    if "enrolment" in DATA_STORE:
        anomalies = detect_anomalies(DATA_STORE["enrolment"])
        if not anomalies.empty:
            return anomalies.to_dict(orient="records")
    return []

@app.get("/api/predictions")
def get_predictions():
    """
    Returns 30-day forecast for enrolment data.
    """
    if "enrolment" in DATA_STORE:
        return predict_future(DATA_STORE["enrolment"])
    return {}

@app.get("/api/map-data")
def get_map_data(category: str = "enrolment"):
    """
    Returns state-wise density for map visualization (latest date or total).
    Category can be: enrolment, demographic, biometric
    """
    # Normalize category to match keys in DATA_STORE
    # e.g. frontend sends "demographic", key is "demographic"
    key = category.lower()
    
    if key in DATA_STORE and not DATA_STORE[key].empty:
        df = DATA_STORE[key]
        # Group by state to get total counts
        state_totals = df.groupby('state').sum(numeric_only=True).reset_index()
        # Sum numeric columns to get proxy for total activity
        numeric_cols = df.select_dtypes(include=['number']).columns
        cols = [c for c in numeric_cols if c != 'pincode']
        
        if not cols:
            return []
            
        state_totals['value'] = state_totals[cols].sum(axis=1)
        
        return state_totals[['state', 'value']].to_dict(orient="records")
    return []

# Serve static files (Frontend)
app.mount("/", StaticFiles(directory="public", html=True), name="static")
