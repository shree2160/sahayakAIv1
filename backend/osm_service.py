"""
Sahayak AI - OpenStreetMap Service
==================================
Fetches nearby places using OpenStreetMap's Overpass API (free).
"""

import logging
from typing import List, Dict, Any, Optional
import math
import httpx

from config import OVERPASS_API_URL, DEFAULT_SEARCH_RADIUS

logger = logging.getLogger(__name__)

# Place type mappings to OSM tags
PLACE_TYPE_MAPPINGS = {
    # Medical
    "hospital": '[amenity=hospital]',
    "clinic": '[amenity=clinic]',
    "pharmacy": '[amenity=pharmacy]',
    "medical_store": '[amenity=pharmacy]',
    
    # Financial
    "bank": '[amenity=bank]',
    "atm": '[amenity=atm]',
    
    # Government/Public
    "post_office": '[amenity=post_office]',
    "police": '[amenity=police]',
    "police_station": '[amenity=police]',
    
    # Education
    "school": '[amenity=school]',
    "college": '[amenity=college]',
    "university": '[amenity=university]',
    
    # Government/CSC Services (India Specific)
    "csc": '[amenity~"public_service|social_facility|government"]',
    "e-seva": '[amenity~"public_service|social_facility|government"]',
    "maha_e-seva_kendra": '[amenity~"public_service|social_facility|government"]',
    "महा_ई-सेवा_केंद्र": '[amenity~"public_service|social_facility|government"]',
    "cyber_cafe": '[amenity=internet_cafe]',
    
    # Transport/Travel
    "petrol": '[amenity=fuel]',
    "petrol_pump": '[amenity=fuel]',
    "railway": '[railway=station]',
    "bus_station": '[amenity=bus_station]',
    
    # Food & Retail
    "restaurant": '[amenity=restaurant]',
    "dhaba": '[amenity=restaurant]',
    "grocery": '[shop=supermarket]',
    "kirana": '[shop=convenience]',
    "general_store": '[shop=convenience]',
    
    # Religious
    "temple": '[amenity=place_of_worship][religion=hindu]',
    "mosque": '[amenity=place_of_worship][religion=muslim]',
    
    # Hindi Labels (Common)
    "अस्पताल": '[amenity=hospital]',
    "बैंक": '[amenity=bank]',
    "पुलिस": '[amenity=police]',
    "मंदिर": '[amenity=place_of_worship][religion=hindu]',
    "किराना": '[shop=convenience]',
}


class OSMService:
    """OpenStreetMap service with mirror fallback to handle timeouts."""
    
    def __init__(self):
        self.default_radius = DEFAULT_SEARCH_RADIUS
        # List of reliable Overpass mirrors
        self.mirrors = [
            "https://overpass-api.de/api/interpreter",
            "https://overpass.kumi.systems/api/interpreter",
            "https://overpass.osm.ch/api/interpreter",
            "https://overpass.nchc.org.tw/api/interpreter"
        ]
    
    def _get_osm_tag(self, place_type: str) -> str:
        place_type_lower = place_type.lower().strip()
        mapped_type = place_type_lower.replace(" ", "_")
        
        if place_type_lower in PLACE_TYPE_MAPPINGS:
            return PLACE_TYPE_MAPPINGS[place_type_lower]
        if mapped_type in PLACE_TYPE_MAPPINGS:
            return PLACE_TYPE_MAPPINGS[mapped_type]
            
        return f'[name~"{place_type}",i]'
    
    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        a = math.sin(delta_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(delta_lambda/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    async def find_nearby(self, latitude: float, longitude: float, place_type: str, 
                          radius: int = None, limit: int = 10) -> List[Dict[str, Any]]:
        radius = radius or self.default_radius
        osm_tag = self._get_osm_tag(place_type)
        query = f"[out:json][timeout:25];(node{osm_tag}(around:{radius},{latitude},{longitude});way{osm_tag}(around:{radius},{latitude},{longitude});relation{osm_tag}(around:{radius},{latitude},{longitude}););out center body;"
        
        logger.info(f"OSM: Searching for '{place_type}' within {radius}m...")
        
        # Try mirrors one by one if they fail
        for mirror_url in self.mirrors:
            try:
                logger.info(f"OSM: Trying mirror: {mirror_url.split('/')[2]}")
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.post(mirror_url, data={"data": query})
                    
                    if response.status_code == 200:
                        data = response.json()
                        elements = data.get("elements", [])
                        logger.info(f"OSM: Success! Received {len(elements)} elements")
                        
                        places = []
                        for el in elements:
                            tags = el.get("tags")
                            if not tags: continue
                            
                            lat = el.get("lat") or (el.get("center", {}).get("lat"))
                            lon = el.get("lon") or (el.get("center", {}).get("lon"))
                            
                            if lat and lon:
                                dist = self._calculate_distance(latitude, longitude, lat, lon)
                                places.append({
                                    "name": tags.get("name") or tags.get("name:hi") or tags.get("operator") or "Unknown Place",
                                    "place_type": tags.get("amenity") or tags.get("shop") or tags.get("leisure") or "place",
                                    "latitude": lat, 
                                    "longitude": lon,
                                    "distance_meters": round(dist, 1),
                                    "phone": tags.get("phone") or tags.get("contact:phone"),
                                    "address": tags.get("addr:full") or tags.get("addr:street") or "Address not available",
                                })
                        
                        places.sort(key=lambda x: x["distance_meters"])
                        unique_places = []
                        seen_names = set()
                        for p in places:
                            if p["name"] not in seen_names:
                                unique_places.append(p)
                                seen_names.add(p["name"])
                        
                        return unique_places[:limit]
                    else:
                        logger.warning(f"OSM: Mirror {mirror_url} returned {response.status_code}")
                        continue # Try next mirror
                        
            except Exception as e:
                logger.warning(f"OSM: Mirror {mirror_url} failed: {str(e)[:50]}")
                continue
                
        logger.error("OSM: All Overpass mirrors failed.")
        return []
    
    def get_status(self) -> dict:
        return {"available": True, "api_url": self.api_url}

_osm_instance: Optional[OSMService] = None

def get_osm_service() -> OSMService:
    global _osm_instance
    if _osm_instance is None:
        _osm_instance = OSMService()
    return _osm_instance
