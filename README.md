# Aadhaar Data Analysis Dashboard

This is a cleaned and refactored version of the original `app_py.py` script.
The original script contained Jupyter Notebook artifacts (`!pip`, `!wget`, `/content/` paths) that prevented it from running locally.

## Features
- Analyses Enrolment, Biometric, and Demographic data.
- Handles missing data gracefully.
- Provides a "Mock Data" generator for demonstration purposes.

## How to Run
1. Ensure you have Python installed.
2. Install dependencies:
   ```powershell
   python -m pip install streamlit pandas matplotlib
   ```
3. Run the app:
   ```powershell
   python -m streamlit run app.py
   ```

## Folder Structure
- `app.py`: The main application code.
- `aadhaar_data/`: The expected directory for input CSV files.
  - `enrolment/`
  - `biometric/`
  - `demographic/`
