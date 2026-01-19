document.addEventListener('DOMContentLoaded', () => {
    setupNavigation();
    setupMapFilter();

    try {
        initMap();
    } catch (e) {
        console.error("Map initialization failed (check internet logic/Leaflet):", e);
    }

    fetchBriefData();
});

function setupNavigation() {
    const navButtons = document.querySelectorAll('nav button');
    if (!navButtons.length) return;

    const sections = {
        'dashboard': ['main-dashboard', 'predictive-dashboard'],
        'regional': ['main-dashboard'],
        'predictive': ['predictive-dashboard']
    };

    navButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Remove active class from all
            navButtons.forEach(b => b.classList.remove('active'));
            // Add to current
            e.target.classList.add('active');

            const viewName = e.target.innerText.trim().toLowerCase();
            const visibleIds = sections[viewName] || sections['dashboard'];

            // Hide all first
            const allIds = new Set(Object.values(sections).flat());
            allIds.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.display = 'none';
            });

            // Show selected
            visibleIds.forEach(id => {
                const el = document.getElementById(id);
                if (el) el.style.display = 'grid';
            });

            // Trigger resize for plots/maps
            setTimeout(() => {
                window.dispatchEvent(new Event('resize'));
                if (map) map.invalidateSize();
            }, 100);
        });
    });
}

function setupMapFilter() {
    const filter = document.getElementById('map-filter');
    if (!filter) return;

    filter.addEventListener('change', (e) => {
        const val = e.target.value;
        console.log("Map filter changed to:", val);
        // Refresh map data based on filter if we had dynamic endpoints
        // For now, re-fetch or just log
        fetchBriefData();
    });
}

let map;

function initMap() {
    // Center of India
    map = L.map('map-container').setView([20.5937, 78.9629], 5);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);
}

async function fetchBriefData(mapCategory = 'enrolment') {
    try {
        // Fetch Trends
        const trendsRes = await fetch('/api/trends');
        const trendsData = await trendsRes.json();

        // Fetch Anomalies
        const anomaliesRes = await fetch('/api/anomalies');
        const anomaliesData = await anomaliesRes.json();

        // Fetch Predictions
        const predRes = await fetch('/api/predictions');
        const predData = await predRes.json();

        // Fetch Map Data with dynamic category
        const mapRes = await fetch(`/api/map-data?category=${mapCategory}`);
        const mapData = await mapRes.json();

        updateKPIs(trendsData, anomaliesData);
        renderCharts(trendsData, predData);
        updateMap(mapData);
        updateAnomalyTable(anomaliesData);

    } catch (error) {
        console.error("Error fetching data:", error);
    }
}

function updateKPIs(trends, anomalies) {
    // Simple logic: sum value arrays for total
    const enrolmentTotal = trends.enrolment?.values.reduce((a, b) => a + b, 0) || 0;
    const demographicTotal = trends.demographic?.values.reduce((a, b) => a + b, 0) || 0;
    const biometricTotal = trends.biometric?.values.reduce((a, b) => a + b, 0) || 0;

    document.getElementById('kpi-enrolment').innerText = enrolmentTotal.toLocaleString();
    document.getElementById('kpi-demographic').innerText = demographicTotal.toLocaleString();
    document.getElementById('kpi-biometric').innerText = biometricTotal.toLocaleString();
    document.getElementById('kpi-anomalies').innerText = anomalies ? anomalies.length : 0;
}

function renderCharts(trends, predictions) {
    // 1. Growth Trends Chart
    const traces = [];

    if (trends.enrolment) {
        traces.push({
            x: trends.enrolment.dates,
            y: trends.enrolment.values,
            name: 'Enrolment',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#38bdf8' }
        });
    }

    if (trends.demographic) {
        traces.push({
            x: trends.demographic.dates,
            y: trends.demographic.values,
            name: 'Demo Updates',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#FB7185' }
        });
    }

    if (trends.biometric) {
        traces.push({
            x: trends.biometric.dates,
            y: trends.biometric.values,
            name: 'Biometric Updates',
            type: 'scatter',
            mode: 'lines',
            line: { color: '#a855f7' }
        });
    }

    const layout = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: { color: '#94a3b8' },
        margin: { t: 20, r: 20, l: 40, b: 40 },
        xaxis: { gridcolor: '#334155' },
        yaxis: { gridcolor: '#334155' }
    };

    Plotly.newPlot('trend-chart', traces, layout, { responsive: true });

    // 2. Forecast Chart
    if (predictions && predictions.dates) {
        const predTrace = {
            x: predictions.dates,
            y: predictions.predicted_values,
            name: 'Forecast',
            type: 'scatter',
            line: { dash: 'dot', color: '#22c55e' }
        };

        Plotly.newPlot('forecast-chart', [predTrace], layout, { responsive: true });
    }
}

// State Coordinates Mapping
const STATE_COORDS = {
    "Andhra Pradesh": { lat: 15.9129, lon: 79.7400 },
    "Arunachal Pradesh": { lat: 28.2180, lon: 94.7278 },
    "Assam": { lat: 26.2006, lon: 92.9376 },
    "Bihar": { lat: 25.0961, lon: 85.3131 },
    "Chhattisgarh": { lat: 21.2787, lon: 81.8661 },
    "Goa": { lat: 15.2993, lon: 74.1240 },
    "Gujarat": { lat: 22.2587, lon: 71.1924 },
    "Haryana": { lat: 29.0588, lon: 76.0856 },
    "Himachal Pradesh": { lat: 31.1048, lon: 77.1734 },
    "Jharkhand": { lat: 23.6102, lon: 85.2799 },
    "Karnataka": { lat: 15.3173, lon: 75.7139 },
    "Kerala": { lat: 10.8505, lon: 76.2711 },
    "Madhya Pradesh": { lat: 22.9734, lon: 78.6569 },
    "Maharashtra": { lat: 19.7515, lon: 75.7139 },
    "Manipur": { lat: 24.6637, lon: 93.9063 },
    "Meghalaya": { lat: 25.4670, lon: 91.3662 },
    "Mizoram": { lat: 23.1645, lon: 92.9376 },
    "Nagaland": { lat: 26.1584, lon: 94.5624 },
    "Odisha": { lat: 20.9517, lon: 85.0985 },
    "Punjab": { lat: 31.1471, lon: 75.3412 },
    "Rajasthan": { lat: 27.0238, lon: 74.2179 },
    "Sikkim": { lat: 27.5330, lon: 88.5122 },
    "Tamil Nadu": { lat: 11.1271, lon: 78.6569 },
    "Telangana": { lat: 18.1124, lon: 79.0193 },
    "Tripura": { lat: 23.9408, lon: 91.9882 },
    "Uttar Pradesh": { lat: 26.8467, lon: 80.9462 },
    "Uttarakhand": { lat: 30.0668, lon: 79.0193 },
    "West Bengal": { lat: 22.9868, lon: 87.8550 },
    "Andaman and Nicobar Islands": { lat: 11.7401, lon: 92.6586 },
    "Chandigarh": { lat: 30.7333, lon: 76.7794 },
    "Dadra and Nagar Haveli": { lat: 20.1809, lon: 73.0169 },
    "Daman and Diu": { lat: 20.4283, lon: 72.8397 },
    "Delhi": { lat: 28.7041, lon: 77.1025 },
    "Jammu and Kashmir": { lat: 33.7782, lon: 76.5762 },
    "Ladakh": { lat: 34.1526, lon: 77.5770 },
    "Lakshadweep": { lat: 10.5667, lon: 72.6417 },
    "Puducherry": { lat: 11.9416, lon: 79.8083 }
};

function initMap() {
    // We will initialize Plotly map in updateMap since it needs data to render the first frame effectively.
    // Or we can render an empty globe here.
    const layout = {
        geo: {
            scope: 'asia',
            projection: { type: 'orthographic' },
            showland: true,
            landcolor: '#1e293b',
            subunitcolor: '#475569',
            countrycolor: '#475569',
            bgcolor: 'rgba(0,0,0,0)',
            center: { lon: 78.9629, lat: 20.5937 },
            projection: {
                type: 'orthographic',
                rotation: { lon: 78, lat: 20 }
            }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 0, r: 0, l: 0, b: 0 },
        height: 400
    };

    // Initial empty plot
    Plotly.newPlot('map-container', [], layout, { displayModeBar: false });
}

function updateMap(mapData) {
    if (!mapData || !mapData.length) return;

    const lats = [];
    const lons = [];
    const texts = [];
    const values = [];

    mapData.forEach(item => {
        const coords = STATE_COORDS[item.state] || STATE_COORDS[item.state.trim()];
        if (coords) {
            lats.push(coords.lat);
            lons.push(coords.lon);
            texts.push(`${item.state}: ${item.value}`);
            values.push(item.value);
        }
    });

    // Normalize marker sizes
    const maxSize = Math.max(...values);
    const sizes = values.map(v => (v / maxSize) * 40 + 5);

    const data = [{
        type: 'scattergeo',
        mode: 'markers',
        lat: lats,
        lon: lons,
        text: texts,
        marker: {
            size: sizes,
            color: values,
            colorscale: 'Viridis',
            cmin: 0,
            cmax: maxSize,
            opacity: 0.8,
            line: {
                color: 'white',
                width: 1
            }
        },
        name: 'Enrolment Data'
    }];

    const layout = {
        geo: {
            scope: 'asia',
            resolution: 50,
            showcoastlines: true,
            coastlinecolor: "#334155",
            showland: true,
            landcolor: "#0f172a",
            showocean: true,
            oceancolor: "#1e293b",
            showlakes: true,
            lakecolor: "#1e293b",
            showcountries: true,
            countrycolor: "#475569",
            center: { lon: 82, lat: 23 }, // Approx center of India
            projection: {
                type: 'orthographic', // 3D Globe effect
                rotation: { lon: 82, lat: 20 }
            }
        },
        paper_bgcolor: 'rgba(0,0,0,0)',
        margin: { t: 0, b: 0, l: 0, r: 0 },
        showlegend: false
    };

    Plotly.react('map-container', data, layout, { displayModeBar: false });
}

function updateAnomalyTable(anomalies) {
    const tbody = document.querySelector('#anomaly-table tbody');
    tbody.innerHTML = '';

    if (!anomalies || anomalies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3">No anomalies detected.</td></tr>';
        return;
    }

    anomalies.slice(0, 10).forEach(a => {
        const row = document.createElement('tr');
        // date is datetime object in python, iso string in json
        const dateStr = a.date ? new Date(a.date).toLocaleDateString() : 'N/A';
        const type = "Volume Spike"; // simpler for now
        const severity = "High";

        row.innerHTML = `
            <td>${dateStr}</td>
            <td>${type}</td>
            <td style="color: #ef4444">${severity}</td>
        `;
        tbody.appendChild(row);
    });
}
