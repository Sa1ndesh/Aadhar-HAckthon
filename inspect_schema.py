import pandas as pd
import os

files = [
    "data/api_data_aadhar_biometric/api_data_aadhar_biometric_0_500000.csv",
    "data/api_data_aadhar_demographic/api_data_aadhar_demographic_0_500000.csv",
    "data/api_data_aadhar_enrolment/api_data_aadhar_enrolment_0_500000.csv"
]

for f in files:
    print(f"--- Schema for {f} ---")
    if os.path.exists(f):
        try:
            df = pd.read_csv(f, nrows=2)
            print(df.columns.tolist())
            print(df.head())
        except Exception as e:
            print(f"Error reading {f}: {e}")
    else:
        print(f"File not found: {f}")
    print("\n")
