import folium
import random
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# India bounds
INDIA_BOUNDS = {
    'min_lat': 8.0, 'max_lat': 37.0,
    'min_lon': 68.0, 'max_lon': 97.0
}
# Reverse geocoding function
geolocator = Nominatim(user_agent="india-map-check")

def is_in_india(lat, lon):
    try:
        location = geolocator.reverse((lat, lon), exactly_one=True, language='en', timeout=10)
        if location and 'India' in location.address:
            return True
    except GeocoderTimedOut:
        pass
    return False

# Generate random valid coordinates within India
def generate_valid_coords(count):
    coords = []
    attempts = 0
    while len(coords) < count and attempts < 500:
        lat = random.uniform(INDIA_BOUNDS['min_lat'], INDIA_BOUNDS['max_lat'])
        lon = random.uniform(INDIA_BOUNDS['min_lon'], INDIA_BOUNDS['max_lon'])
        if is_in_india(lat, lon):
            coords.append((lat, lon))
        attempts += 1
        time.sleep(1)  # To avoid hitting geocoding rate limit
    return coords
# Generate 15 issue locations
issue_coords = generate_valid_coords(15)
issue_types = ["Pothole", "Garbage", "Street Light", "Water Supply", "Sewage"]
issues = []
for i, (lat, lon) in enumerate(issue_coords):
    priority = random.choice(["high", "medium", "low"])
    issues.append({
        "lat": lat,
        "lon": lon,
        "priority": priority,
        "type": random.choice(issue_types)
    })

m_issues = folium.Map(location=[22.0, 79.0], zoom_start=5)
for issue in issues:
    color = "red" if issue["priority"] == "high" else "orange" if issue["priority"] == "medium" else "blue"
    folium.Marker(
        [issue["lat"], issue["lon"]],
        popup=f"{issue['type']} ({issue['priority']})",
        icon=folium.Icon(color=color)
    ).add_to(m_issues)
m_issues.save("issues_map_india.html")

print("Maps saved! All markers are now strictly within India.")