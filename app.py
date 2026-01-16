
import streamlit as st
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Set page config
st.set_page_config(page_title="Aadhaar Analytics Suite", layout="wide")

st.title("Aadhaar Data Analysis & Forecasting")

# Define Data Directory
DATA_DIR = "aadhaar_data"

def clean_columns(df):
    """Standardize column names and remove duplicates."""
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    # Remove duplicate columns, keeping the first occurrence
    df = df.loc[:, ~df.columns.duplicated()]
    return df

def read_all_csv(folder_path):
    """Read all CSVs from a folder recursively."""
    df_list = []
    if not os.path.exists(folder_path):
        return pd.DataFrame()
    
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.csv'):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    df_list.append(df)
                except Exception as e:
                    st.warning(f"Could not read {file}: {e}")
    
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    return pd.DataFrame()

def preprocess_data(df, name="df"):
    """
    Standardize dates, create month_year, and calculate enrollment_count.
    """
    if df.empty:
        return df
    
    df = clean_columns(df)
    
    # 1. Date Handling
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df["month_year"] = df["date"].dt.to_period("M").astype(str)
    elif "year" in df.columns and "month" in df.columns:
        df["month_year"] = df["year"].astype(str) + "-" + df["month"].astype(str)
        # Create a dummy date for sorting (1st of the month)
        df["date"] = pd.to_datetime(df["month_year"] + "-01", errors="coerce")
    
    # 2. Enrolment Count Calculation
    # Combines bio_age_5_17 and bio_age_17_
    age_cols = ["bio_age_5_17", "bio_age_17_"]
    existing_age_cols = [c for c in age_cols if c in df.columns]
    
    if existing_age_cols:
        df["enrolment_count"] = df[existing_age_cols].sum(axis=1)
        # st.success(f"Calculated 'enrolment_count' for {name} using {existing_age_cols}")
    elif "count" in df.columns:
         df["enrolment_count"] = df["count"]
    
    # 3. Sort Chronologically
    if "date" in df.columns:
        df = df.sort_values("date")
        
    return df

# --- UI Layout ---
st.sidebar.header("Configuration")
data_root = st.sidebar.text_input("Data Root Directory", value=DATA_DIR)

st.write(f"Looking for data in: `{os.path.abspath(data_root)}`")

# Load Data
with st.spinner("Loading and Processing Data..."):
    # We primarily focus on 'Enrolment' or 'Aadhaar Data' which contains the bio_age columns
    # Based on file structure, we try to load all and see which one has the target columns
    
    enrol = read_all_csv(os.path.join(data_root, "enrolment"))
    bio = read_all_csv(os.path.join(data_root, "biometric"))
    demo = read_all_csv(os.path.join(data_root, "demographic"))
    
    # If standard folders fail, try loading everything from root if user pointed there
    extra = pd.DataFrame()
    if enrol.empty and bio.empty and demo.empty:
         extra = read_all_csv(data_root)

# Combine for easier search
dfs = {
    "Enrolment": enrol, 
    "Biometric": bio, 
    "Demographic": demo,
    "Combined/Extra": extra
}

valid_df = None
df_name = ""

# Find the main dataframe that has enrolment counts
for name, df in dfs.items():
    if not df.empty:
        df = preprocess_data(df, name)
        if "enrolment_count" in df.columns:
            valid_df = df
            df_name = name
            break # Use the first one that works

if valid_df is not None:
    st.success(f"Active Dataset: {df_name} ({valid_df.shape[0]} rows)")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "EDA & Trends", 
        "Age Group Analysis", 
        "Anomaly Detection", 
        "Forecasting", 
        "Recommendations"
    ])
    
    # --- TAB 1: EDA & Trends ---
    with tab1:
        st.subheader("State-wise Enrolment Distribution")
        if "state" in valid_df.columns:
            state_counts = valid_df.groupby("state")["enrolment_count"].sum().sort_values(ascending=False)
            st.bar_chart(state_counts)
        
        st.subheader("Temporal Trend")
        if "date" in valid_df.columns:
            monthly_trend = valid_df.groupby("date")["enrolment_count"].sum()
            st.line_chart(monthly_trend)
        elif "month_year" in valid_df.columns:
             # Fallback if date parsing failed but string exists
             st.warning("Using string dates (no datetime conversion found)")
             monthly_trend = valid_df.groupby("month_year")["enrolment_count"].sum()
             st.bar_chart(monthly_trend)

    # --- TAB 2: Age Group Analysis ---
    with tab2:
        st.subheader("Enrolment by Age Group")
        age_cols = ["bio_age_5_17", "bio_age_17_"]
        present_cols = [c for c in age_cols if c in valid_df.columns]
        
        if len(present_cols) >= 2:
            totals = valid_df[present_cols].sum()
            st.bar_chart(totals)
            
            st.write("Distribution Ratio:")
            st.write(totals / totals.sum())
        else:
            st.info("Age group columns (bio_age_5_17, bio_age_17_) not found in dataset.")

    # --- TAB 3: Anomaly Detection ---
    with tab3:
        st.subheader("Anomaly Detection (Z-Score)")
        
        # Calculate Z-Score on State-Level Monthly Data
        if "state" in valid_df.columns and "date" in valid_df.columns:
            # Group by State and Date first
            grouped = valid_df.groupby(["state", "date"])["enrolment_count"].sum().reset_index()
            
            # Calculate Mean and Std Dev per State
            stats = grouped.groupby("state")["enrolment_count"].agg(['mean', 'std']).reset_index()
            merged = grouped.merge(stats, on="state")
            
            # Avoid division by zero
            merged["std"] = merged["std"].replace(0, 1)
            
            merged["z_score"] = (merged["enrolment_count"] - merged["mean"]) / merged["std"]
            
            # Anomalies: Z > 3 or Z < -3
            anomalies = merged[abs(merged["z_score"]) > 3]
            
            st.write(f"Detected {len(anomalies)} anomalies (Z-score > 3)")
            if not anomalies.empty:
                st.dataframe(anomalies.sort_values("z_score", ascending=False))
                
                # Plot anomalies for a selected state
                target_state = st.selectbox("Select State to View Anomalies", anomalies["state"].unique())
                state_data = merged[merged["state"] == target_state]
                
                fig, ax = plt.subplots(figsize=(10, 4))
                ax.plot(state_data["date"], state_data["enrolment_count"], label="Enrolment")
                
                # Highlight anomalies
                state_anoms = anomalies[anomalies["state"] == target_state]
                ax.scatter(state_anoms["date"], state_anoms["enrolment_count"], color="red", label="Anomaly")
                
                plt.legend()
                st.pyplot(fig)
        else:
            st.warning("Need 'state' and 'date' columns for granular anomaly detection.")

    # --- TAB 4: Forecasting ---
    with tab4:
        st.subheader("Predictive Analysis (Linear Regression)")
        
        if "date" in valid_df.columns:
            # Aggregate to global trend for simplicity, or per state
            daily_agg = valid_df.groupby("date")["enrolment_count"].sum().reset_index()
            daily_agg["ordinal_date"] = daily_agg["date"].map(pd.Timestamp.toordinal)
            
            X = daily_agg[["ordinal_date"]]
            y = daily_agg["enrolment_count"]
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict next 30 steps (approx 1 month if daily, or just next steps)
            # If data is monthly, this predicts next months. If data is chaotic, it's just a trend line.
            
            future_days = 90 # Predict 3 months ahead
            last_date = daily_agg["date"].max()
            future_dates = [last_date + pd.Timedelta(days=x) for x in range(1, future_days, 30)] # Monthly steps
            future_ordinals = [[pd.Timestamp(d).toordinal()] for d in future_dates]
            
            predictions = model.predict(future_ordinals)
            
            st.write("Forecast for next 3 months:")
            forecast_df = pd.DataFrame({"Date": future_dates, "Predicted_Enrolment": predictions})
            st.dataframe(forecast_df)
            
            # Plot
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            ax2.plot(daily_agg["date"], y, label="Historical")
            ax2.plot(future_dates, predictions, label="Forecast", linestyle="--", color="orange")
            plt.legend()
            st.pyplot(fig2)
        else:
            st.warning("Time-series forecasting requires a valid date column.")

    # --- TAB 5: Recommendations ---
    with tab5:
        st.subheader("Policy & Operational Recommendations")
        
        # Simple Logic-Based Recommendations
        if "state" in valid_df.columns:
             total_per_state = valid_df.groupby("state")["enrolment_count"].sum()
             low_performers = total_per_state.nsmallest(5)
             high_performers = total_per_state.nlargest(5)
             
             st.markdown("### 🔴 Regions Requiring Attention")
             st.write("The following states have the lowest enrolment counts. Consider **targeted awareness campaigns** and **mobile enrolment units**:")
             for state, count in low_performers.items():
                 st.write(f"- **{state}**: {count:,.0f}")
                 
             st.markdown("### 🟢 High Growth Models")
             st.write("These states are performing well. Their strategies could be replicated:")
             for state, count in high_performers.items():
                 st.write(f"- **{state}**: {count:,.0f}")

else:
    st.error("No valid data found. Please check the directory path or generate mock data.")
    # Mock data creation for demonstration if real data is missing
    create_mock = st.button("Generate Mock Data for Testing")
    
    if create_mock:
        os.makedirs(os.path.join(data_root, "enrolment"), exist_ok=True)
        # Create sample CSVs with the RIGHT columns
        df_sample = pd.DataFrame({
            "state": ["Delhi", "Mumbai", "Karnataka"] * 10,
            "date": pd.date_range("2023-01-01", periods=30).tolist() * 1,
            "bio_age_5_17": np.random.randint(50, 200, 30),
            "bio_age_17_": np.random.randint(100, 500, 30)
        })
        df_sample.to_csv(os.path.join(data_root, "enrolment", "sample_mock.csv"), index=False)
        st.success(f"Mock data created in {data_root}. Please Refresh!")

