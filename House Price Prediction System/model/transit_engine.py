def calculate_transit_score(dist_metro_km, dist_railway_km, dist_highway_km):
    """
    Calculates a normalized transit accessibility score (0 to 100)
    for Indian cities based on proximity to Metro, Suburban Rail, and Highways.
    """
    metro_score = max(0, 100 - (dist_metro_km * 15))
    railway_score = max(0, 100 - (dist_railway_km * 10))
    highway_score = max(0, 100 - (dist_highway_km * 8))
    
    total_score = (metro_score * 0.50) + (railway_score * 0.30) + (highway_score * 0.20)
    return round(total_score, 2)

def get_transit_category(score):
    if score >= 80:
        return "Excellent Connectivity (Near Metro/Rail)"
    elif score >= 60:
        return "Good Connectivity"
    elif score >= 40:
        return "Moderate Connectivity"
    else:
        return "Low Connectivity / Outskirts"