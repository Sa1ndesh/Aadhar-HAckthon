from fastapi.testclient import TestClient
from src.main import app
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

client = TestClient(app)

if __name__ == "__main__":
    with TestClient(app) as client:
        # Re-define functions or call them passing client? 
        # Easier to just inline or pass client.
        
        print("Testing Root...")
        response = client.get("/")
        assert response.status_code == 200
        print("PASSED: /")

        endpoints = ["/api/trends", "/api/anomalies", "/api/predictions", "/api/map-data"]
        for ep in endpoints:
            print(f"Testing {ep}...")
            response = client.get(ep)
            if response.status_code != 200:
                print(f"FAILED: {ep} returned {response.status_code}")
                print(response.text)
            else:
                print(f"PASSED: {ep}")
                print(str(response.json())[:100] + "...")
