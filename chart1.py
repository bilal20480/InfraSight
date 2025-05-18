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

# Generate 10 construction sites
construction_coords = generate_valid_coords(10)
construction_data = []
for i, (lat, lon) in enumerate(construction_coords):
    status = random.choice(["ongoing", "completed", "incomplete"])
    progress = random.randint(0, 100) if status != "completed" else 100
    construction_data.append({
        "name": f"Project {i+1}",
        "lat": lat,
        "lon": lon,
        "status": status,
        "progress": progress
    })

m_construction = folium.Map(location=[22.0, 79.0], zoom_start=5)
for site in construction_data:
    color = "orange" if site["status"] == "ongoing" else "green" if site["status"] == "completed" else "red"
    folium.Marker(
        [site["lat"], site["lon"]],
        popup=f"{site['name']} - {site['progress']}% ({site['status']})",
        icon=folium.Icon(color=color)
    ).add_to(m_construction)
m_construction.save("construction_map_india.html")