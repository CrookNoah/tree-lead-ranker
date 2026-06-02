"""Google Places API integration"""
import requests
import time
from typing import List, Dict
from config import GOOGLE_PLACES_API_KEY, SEARCH_TERMS
import logging

logger = logging.getLogger(__name__)

class GooglePlacesAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        self.text_search_url = f"{self.base_url}/textsearch/json"
        self.details_url = f"{self.base_url}/details/json"
        self.rate_limit = 0.5  # seconds between requests
        self.last_request = 0
    
    def _rate_limit(self):
        """Respect rate limits"""
        elapsed = time.time() - self.last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request = time.time()
    
    def search_businesses(self, query: str, location: str, radius: int = 50000) -> List[Dict]:
        """
        Search for businesses using Google Places Text Search API
        radius in meters (50km default)
        """
        self._rate_limit()
        
        params = {
            "query": query,
            "location": location,  # lat,lng
            "radius": radius,
            "key": self.api_key,
        }
        
        try:
            response = requests.get(self.text_search_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Google Places API error: {data.get('status')} - {data.get('error_message')}")
                return []
            
            results = data.get("results", [])
            logger.info(f"Found {len(results)} results for '{query}' near {location}")
            
            # Get next page results if available
            while data.get("next_page_token"):
                time.sleep(2)  # Google requires 2 second delay between pages
                self._rate_limit()
                
                params["pagetoken"] = data["next_page_token"]
                response = requests.get(self.text_search_url, params=params)
                response.raise_for_status()
                data = response.json()
                results.extend(data.get("results", []))
            
            return results
        
        except requests.RequestException as e:
            logger.error(f"Google Places API request error: {e}")
            return []
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a specific place"""
        self._rate_limit()
        
        params = {
            "place_id": place_id,
            "fields": "name,formatted_address,formatted_phone_number,website,rating,review_count,types,url,business_status",
            "key": self.api_key,
        }
        
        try:
            response = requests.get(self.details_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                logger.warning(f"Google Places details error: {data.get('status')}")
                return {}
            
            return data.get("result", {})
        
        except requests.RequestException as e:
            logger.error(f"Google Places details error: {e}")
            return {}
    
    def parse_result(self, result: Dict) -> Dict:
        """Parse a search result into our business format"""
        return {
            "place_id": result.get("place_id"),
            "business_name": result.get("name"),
            "phone": result.get("formatted_phone_number", ""),
            "address": result.get("formatted_address", ""),
            "rating": result.get("rating"),
            "review_count": result.get("user_ratings_total", 0),
            "website_url": result.get("website", ""),
            "google_listing_url": result.get("url", ""),
            "category": result.get("types", []),
            "source": "google_places",
        }
    
    def search_city(self, city: str, state: str, state_code: str) -> List[Dict]:
        """Search all tree service terms for a given city"""
        location_str = f"{city}, {state}"
        all_results = {}
        
        logger.info(f"Searching {location_str} for tree service businesses...")
        
        for term in SEARCH_TERMS:
            query = f"{term} {city} {state}"
            results = self.search_businesses(query, location_str)
            
            for result in results:
                place_id = result.get("place_id")
                if place_id not in all_results:
                    parsed = self.parse_result(result)
                    parsed["city"] = city
                    parsed["state"] = state_code
                    all_results[place_id] = parsed
                    logger.debug(f"Added: {parsed['business_name']}")
            
            time.sleep(0.5)  # Small delay between searches
        
        logger.info(f"Total unique businesses found: {len(all_results)}")
        return list(all_results.values())


def get_places_api() -> GooglePlacesAPI:
    """Factory function to create API instance"""
    if not GOOGLE_PLACES_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not set in .env")
    return GooglePlacesAPI(GOOGLE_PLACES_API_KEY)
