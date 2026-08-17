import os
import pandas as pd
import numpy as np

def generate_indian_housing_data(num_samples=2500, seed=42):
    np.random.seed(seed)
    
    # Base rate per sq. ft. in INR for major Indian cities
    cities_locality_tier = {
        'Mumbai': 18000,
        'Delhi NCR': 9000,
        'Bengaluru': 8000,
        'Pune': 6500,
        'Hyderabad': 7000,
        'Chennai': 6000,
        'Kolkata': 5000,
        'Ahmedabad': 4500
    }
    
    city_choices = list(cities_locality_tier.keys())
    cities = np.random.choice(city_choices, size=num_samples)
    
    bhk = np.random.choice([1, 2, 3, 4], size=num_samples, p=[0.25, 0.45, 0.22, 0.08])
    
    # Calculate square footage relative to BHK
    size_sqft = []
    for b in bhk:
        if b == 1: size = np.random.randint(400, 650)
        elif b == 2: size = np.random.randint(700, 1100)
        elif b == 3: size = np.random.randint(1100, 1800)
        else: size = np.random.randint(1800, 3000)
        size_sqft.append(size)
    size_sqft = np.array(size_sqft)

    property_type = np.random.choice(['Apartment', 'Independent House', 'Builder Floor'], size=num_samples, p=[0.75, 0.15, 0.10])
    furnishing = np.random.choice(['Unfurnished', 'Semi-Furnished', 'Fully Furnished'], size=num_samples, p=[0.3, 0.5, 0.2])
    possession_status = np.random.choice(['Ready to Move', 'Under Construction'], size=num_samples, p=[0.7, 0.3])
    
    # Transit proximity metrics in KM
    dist_metro_km = np.round(np.random.exponential(scale=2.5, size=num_samples), 2)
    dist_railway_km = np.round(np.random.exponential(scale=4.0, size=num_samples), 2)
    dist_highway_km = np.round(np.random.exponential(scale=3.0, size=num_samples), 2)
    
    # Target: Price in Lakhs INR
    prices_lakhs = []
    for i in range(num_samples):
        c = cities[i]
        base_price_sqft = cities_locality_tier[c]
        
        furnish_mult = 1.0 if furnishing[i] == 'Unfurnished' else (1.08 if furnishing[i] == 'Semi-Furnished' else 1.18)
        type_mult = 1.0 if property_type[i] == 'Apartment' else 1.25
        
        # Proximity advantage (closer to transit = higher price)
        transit_bonus = max(0, (5 - dist_metro_km[i]) * 0.03) + max(0, (8 - dist_railway_km[i]) * 0.015)
        
        rate_per_sqft = base_price_sqft * (1 + transit_bonus) * furnish_mult * type_mult
        noise = np.random.normal(1.0, 0.08)
        
        total_price_inr = size_sqft[i] * rate_per_sqft * noise
        price_lakhs = np.round(total_price_inr / 100000, 2)
        prices_lakhs.append(price_lakhs)

    df = pd.DataFrame({
        'City': cities,
        'BHK': bhk,
        'Size_SqFt': size_sqft,
        'Property_Type': property_type,
        'Furnishing': furnishing,
        'Possession_Status': possession_status,
        'Distance_Metro_KM': dist_metro_km,
        'Distance_Railway_KM': dist_railway_km,
        'Distance_Highway_KM': dist_highway_km,
        'Price_Lakhs': prices_lakhs
    })
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/indian_houses_transit.csv', index=False)
    print("Dataset generated and saved to 'data/indian_houses_transit.csv'")

if __name__ == '__main__':
    generate_indian_housing_data()