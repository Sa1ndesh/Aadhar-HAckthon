# Aadhaar Societal Trends - Insight System 📊🇮🇳

**Unlocking Societal Trends in Aadhaar Enrolment and Updates**

A full-stack data analytics platform designed to provide deep insights into Aadhaar saturation, demographic updates, and biometric trends across India. This application processes large-scale datasets to visualize regional density, detect anomalies, and forecast future trends using machine learning techniques.

---

## 🚀 Key Features

*   **Interactive Dashboard**: Real-time KPI cards showing total enrolments, demographic updates, and biometric updates.
*   **Geospatial Visualization**: Interactive 3D/2D map of India (powered by Leaflet) visualizing data density across states.
*   **Trend Analytics**: Dynamic line charts (Plotly) displaying growth trends over time.
*   **Predictive Modeling**: 30-day forecasting of enrolment trends.
*   **Anomaly Detection**: Automated system to flag potential irregularities in data patterns.
*   **Scalable Backend**: Built with **FastAPI** for high-performance data serving.
*   **Responsive Design**: Modern, premium UI styled with custom CSS and animations.

---

## 🛠️ Technology Stack

### Backend
*   **Language**: Python 3.9+
*   **Framework**: FastAPI
*   **Server**: Uvicorn
*   **Data Processing**: Pandas, NumPy
*   **ML/Analytics**: Scikit-Learn (implied), Custom Analytics Modules

### Frontend
*   **Structure**: HTML5, Semantic Web
*   **Styling**: Vanilla CSS3 (Glassmorphism, Dark/Light mode compatible), Google Fonts (Outfit)
*   **Scripting**: Vanilla JavaScript (ES6+)
*   **Visualization**: Plotly.js
*   **Maps**: Leaflet.js (OpenStreetMap tiles)

---

## 📂 Project Structure

```
aadhaar_project/
├── data/                       # Data storage (ZIPs and extracted CSVs)
├── public/                     # Frontend Static Files
│   ├── index.html              # Main Dashboard
│   ├── style.css               # Premium Styling
│   └── script.js               # Frontend Logic & API Integration
├── src/                        # Backend Source Code
│   ├── main.py                 # FastAPI Application & Routes
│   ├── analytics.py            # Analytics, ML, and Statistics Logic
│   └── data_loader.py          # Data Ingestion & Processing Pipeline
├── run_project.py              # Main Entry Point to Start Server
├── setup_data.py               # Script to Unzip/Prepare Data
├── requirements.txt            # Python Dependencies
└── README.md                   # Project Documentation
```

---

## ⚙️ Installation & Setup

### Prerequisites
*   Python 3.8 or higher installed.
*   Pip (Python Package Installer).

### Steps

1.  **Clone/Download the Repository**
    ```bash
    git clone https://github.com/yourusername/aadhaar-trends.git
    cd aadhaar_project
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Prepare Data**
    The project comes with compressed datasets. Run the setup script to extract them:
    ```bash
    python setup_data.py
    ```

4.  **Run the Application**
    Start the local development server:
    ```bash
    python run_project.py
    ```

5.  **Access the Dashboard**
    Open your browser and navigate to:
    **[http://localhost:8000](http://localhost:8000)**

---

## 📡 API Endpoints

The backend provides a RESTful API for consuming data:

*   `GET /api/trends`: returns aggregated time-series data for enrolments and updates.
*   `GET /api/map-data?category={type}`: returns state-wise density data.
    *   *category*: `enrolment` (default), `demographic`, `biometric`.
*   `GET /api/anomalies`: returns a list of detected data anomalies.
*   `GET /api/predictions`: returns forecasted data points for the next 30 days.

---

## 🧪 Testing

To run the API test suite:
```bash
python test_api.py
```

---

## 🔮 Future Roadmap

*   [ ] Integration with live UIDAI open data APIs.
*   [ ] Advanced granular filtering (District/Sub-district level).
*   [ ] Exportable reports (PDF/Excel).
*   [ ] User authentication for admin panels.

---

## 📝 License

This project is open-source and available for educational and hackathon purposes.
