import zipfile
import os

def unzip_data():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    zip_files = [
        "api_data_aadhar_biometric.zip",
        "api_data_aadhar_demographic.zip",
        "api_data_aadhar_enrolment.zip"
    ]
    
    for zf in zip_files:
        if os.path.exists(zf):
            print(f"Unzipping {zf}...")
            with zipfile.ZipFile(zf, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
        else:
            print(f"Warning: {zf} not found.")

if __name__ == "__main__":
    unzip_data()
