import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression

def calculate_state_growth(df):
    """
    Calculates the total enrolment/update count per state over time.
    Expects df to have 'date' and 'state' columns.
    """
    if df.empty or 'date' not in df.columns or 'state' not in df.columns:
        return pd.DataFrame()
        
    # Group by state and date
    trend = df.groupby(['state', 'date']).size().reset_index(name='count')
    # Or if we need to sum specific columns (e.g. age groups), we should do that.
    # Based on schema, we have counts in columns.
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cols_to_sum = [c for c in numeric_cols if c not in ['pincode']]
    
    if cols_to_sum:
        trend = df.groupby(['state', 'date'])[cols_to_sum].sum().reset_index()
        trend['total'] = trend[cols_to_sum].sum(axis=1)
    else:
        trend = df.groupby(['state', 'date']).size().reset_index(name='total')
        
    return trend

def detect_anomalies(df):
    """
    Detects anomalies in the daily total counts across the entire dataset (or per state).
    Uses Isolation Forest.
    """
    if df.empty or 'date' not in df.columns:
        return pd.DataFrame()

    # Aggregate by date globally for now
    daily_counts = df.groupby('date').sum(numeric_only=True).reset_index()
    # sum all numeric columns to get a 'total' activity proxy
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cols_to_sum = [c for c in numeric_cols if c != 'pincode']
    
    if not cols_to_sum:
        return pd.DataFrame()
        
    daily_counts['total_activity'] = daily_counts[cols_to_sum].sum(axis=1)
    
    if len(daily_counts) < 10: # Not enough data for anomaly detection
        return pd.DataFrame()
        
    iso = IsolationForest(contamination=0.05, random_state=42)
    daily_counts['anomaly_score'] = iso.fit_predict(daily_counts[['total_activity']])
    
    # -1 indicates anomaly
    anomalies = daily_counts[daily_counts['anomaly_score'] == -1]
    return anomalies

def predict_future(df, days=30):
    """
    Predicts future demand using simple Linear Regression on time.
    """
    if df.empty or 'date' not in df.columns:
        return {}

    # Aggregate daily
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    cols_to_sum = [c for c in numeric_cols if c != 'pincode']
    
    if not cols_to_sum:
        return {}
        
    daily = df.groupby('date')[cols_to_sum].sum().reset_index()
    daily['total'] = daily[cols_to_sum].sum(axis=1)
    
    # Prepare X (ordinal dates) and y
    daily['date_ordinal'] = daily['date'].map(pd.Timestamp.toordinal)
    
    X = daily[['date_ordinal']]
    y = daily['total']
    
    if len(X) < 5:
        return {}
        
    model = LinearRegression()
    model.fit(X, y)
    
    last_date = daily['date'].max()
    future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, days+1)]
    future_ordinals = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    
    predictions = model.predict(future_ordinals)
    
    return {
        "dates": [d.strftime('%Y-%m-%d') for d in future_dates],
        "predicted_values": predictions.tolist()
    }
