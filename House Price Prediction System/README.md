# House Price Prediction System with Transit Proximity

## Overview
A complete, production-ready House Price Prediction System that incorporates transit proximity (distance to Metro, Subway, and Railway stations) as a key feature that increases property valuation.

## Project Structure
```
├── data/
│   ├── generate_dataset.py   # Generates realistic spatial housing & transit station data
│   └── houses_transit.csv    # Generated dataset with station proximity features
├── model/
│   ├── train_model.py        # ML training script with cross-validation & metrics (MAE, RMSE, R2)
│   ├── transit_engine.py      # Spatial & geocoding helper (Haversine distance & transit score generator)
│   └── house_price_model.pkl # Trained ML model binary
├── app.py                    # Streamlit web application dashboard with interactive maps
├── requirements.txt          # Clean dependencies file
└── README.md                 # Setup and run instructions
```

## Installation

1. **Clone the repository** or download the project files.

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the data generation script** (first-time setup or to regenerate data):
   ```bash
   python data/generate_dataset.py
   ```
   This generates `data/houses_transit.csv` with 2,000 house records and 15 fixed transit stations.

4. **Train the ML model**:
   ```bash
   python model/train_model.py
   ```
   This trains an XGBoost regression model using the generated dataset and saves:
   - `model/house_price_model.pkl` - Trained model
   - `model/scaler.pkl` - Fitted preprocessor (scaler + one-hot encoder)

5. **Start the Streamlit dashboard**:
   ```bash
   streamlit run app.py
   ```
   The app will be available at `http://localhost:8501`

## Features

### Transit Proximity Price Premium
- **Haversine distance calculation**: Computes the great-circle distance in kilometers between house GPS coordinates and the nearest transit station
- **Exponential decay pricing model**: Houses closer than 500m get up to a 20% value surge; the price effect decays smoothly with distance
- **Transit accessibility scoring**: 0-100 scale based on distance bands:
  - `< 500m`: Score 100 (excellent access)
  - `0.5–1.0km`: Score 80-99 (good access)
  - `1.0–2.0km`: Score 50-79 (moderate access)
  - `2.0–5.0km`: Score 20-49 (poor access)
  - `> 5.0km`: Score 0-19 (very poor access)

### Machine Learning Pipeline
- **Algorithm**: XGBoost Regressor
- **Features**: `square_feet`, `bedrooms`, `bathrooms`, `year_built`, `garage_spaces`, `log_sqft`, `age_of_home`, `min_distance_to_transit_km`, `transit_score`, `distance_band`, `nearest_station_type`
- **Preprocessing**: Standard scaling for numeric features, OneHotEncoding for categorical features
- **Evaluation**: MAE, RMSE, R2 with 5-fold cross-validation
- Metrics achieved on test set: MAE ~$4,976, RMSE ~$8,652, R2 ~0.999

### Interactive Web Dashboard
- **House specifications**: Slider inputs for square feet, bedrooms, bathrooms, year built, garage spaces
- **Location input**: Manual lat/lon entry or click on map
- **Price display**: Estimated house price with transit premium dollar amount and accessibility score
- **Interactive Folium map**: Shows house pin (green), nearby transit stations (blue train icons), and connecting distance lines
- **What-If Transit Simulator**: Slider to test "What if a new subway station is built X meters away?" showing instant valuation increase/decrease percentage

## Dependencies
See `requirements.txt` for the full list:
- streamlit, streamlit-folium, folium, pandas, numpy, scikit-learn, xgboost, geopy, joblib

## Generated Dataset
The `data/houses_transit.csv` contains 2,000 house records with the following columns:
- `house_id`: Unique identifier
- `latitude`, `longitude`: GPS coordinates
- `square_feet`, `bedrooms`, `bathrooms`, `year_built`, `garage_spaces`: Structural features
- `distance_to_metro_km`, `distance_to_subway_km`, `distance_to_rail_km`: Distance to each transit type
- `min_distance_to_transit_km`: Minimum distance to any transit station
- `nearest_station_name`, `nearest_station_type`: Nearest station details
- `transit_score`: 0-100 accessibility score
- `transit_multiplier`: Price multiplier factor
- `price`: Target variable (base price + transit premium)
- `price_per_sqft`: Price per square foot