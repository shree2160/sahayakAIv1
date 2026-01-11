"""
Sahayak AI - Location Service
=============================
Handles location detection, geocoding, and coordinate processing.
"""

import logging
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

# Major Indian cities with coordinates
INDIAN_CITIES = {
    "delhi": (28.6139, 77.2090),
    "mumbai": (19.0760, 72.8777),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "pune": (18.5204, 73.8567),
    "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873),
    "lucknow": (26.8467, 80.9462),
    "kanpur": (26.4499, 80.3319),
    "nagpur": (21.1458, 79.0882),
    "patna": (25.5941, 85.1376),
    "indore": (22.7196, 75.8577),
    "bhopal": (23.2599, 77.4126),
    "noida": (28.5355, 77.3910),
    "gurgaon": (28.4595, 77.0266),
    "gurugram": (28.4595, 77.0266),
    "दिल्ली": (28.6139, 77.2090),
    "मुंबई": (19.0760, 72.8777),
    "कोलकाता": (22.5726, 88.3639),
}

# Default location (Delhi)
DEFAULT_LOCATION = (28.6139, 77.2090)


class LocationService:
    """Handles location detection and geocoding."""
    
    def __init__(self):
        self.default_lat, self.default_lon = DEFAULT_LOCATION
    
    def extract_location_from_text(self, text: str) -> Optional[Tuple[float, float]]:
        """Extract coordinates from city name in text."""
        text_lower = text.lower()
        for city, coords in INDIAN_CITIES.items():
            if city in text_lower:
                logger.info(f"Found city: {city}")
                return coords
        return None
    
    def get_location(self, latitude: float = None, longitude: float = None, 
                     text: str = None) -> Tuple[float, float, str]:
        """Get location from coords or text, with fallback."""
        if latitude and longitude:
            return latitude, longitude, "provided"
        if text:
            coords = self.extract_location_from_text(text)
            if coords:
                return coords[0], coords[1], "extracted"
        return self.default_lat, self.default_lon, "default"
    
    def get_city_name(self, lat: float, lon: float) -> str:
        """Get approximate city name from coordinates."""
        min_dist = float('inf')
        closest = "Unknown"
        for city, (city_lat, city_lon) in INDIAN_CITIES.items():
            if not any('\u0900' <= c <= '\u097F' for c in city):  # Skip Hindi names
                dist = ((lat - city_lat)**2 + (lon - city_lon)**2)**0.5
                if dist < min_dist:
                    min_dist, closest = dist, city.title()
        return closest
    
    def get_status(self) -> dict:
        return {"available": True, "cities_count": len(INDIAN_CITIES)}

_location_instance: Optional[LocationService] = None

def get_location_service() -> LocationService:
    global _location_instance
    if _location_instance is None:
        _location_instance = LocationService()
    return _location_instance
