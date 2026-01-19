import pandas as pd
import os
import glob

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_category_data(category_folder):
    """
    Loads all CSV files from a specific category folder and merges them.
    Expects folder structure: data/api_data_aadhar_<category>/...
    """
    path = os.path.join(DATA_DIR, category_folder, "*.csv")
    all_files = glob.glob(path)
    
    if not all_files:
        print(f"Warning: No files found in {path}")
        return pd.DataFrame()
    
    df_list = []
    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            df_list.append(df)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    unified_df = pd.concat(df_list, ignore_index=True)
    
    # Standardize column names: strip whitespace, lowercase
    unified_df.columns = [c.strip().lower() for c in unified_df.columns]
    
    # Convert date to datetime if 'date' column exists
    if 'date' in unified_df.columns:
        unified_df['date'] = pd.to_datetime(unified_df['date'], format='%d-%m-%Y', errors='coerce')
        
    return unified_df

def load_all_data():
    """
    Loads enrolment, demographic, and biometric data.
    Returns a dictionary of DataFrames.
    """
    print("Loading Enrolment Data...")
    enrolment_df = load_category_data("api_data_aadhar_enrolment")
    
    print("Loading Demographic Data...")
    demographic_df = load_category_data("api_data_aadhar_demographic")
    
    print("Loading Biometric Data...")
    biometric_df = load_category_data("api_data_aadhar_biometric")
    
    return {
        "enrolment": enrolment_df,
        "demographic": demographic_df,
        "biometric": biometric_df
    }

if __name__ == "__main__":
    # Test run
    data = load_all_data()
    for key, df in data.items():
        print(f"\n--- {key.upper()} DATA ---")
        print(f"Shape: {df.shape}")
        print(df.head())
        print(df.dtypes)
