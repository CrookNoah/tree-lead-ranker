"""
Enhanced Business Scraper

Maximizes coverage using:
1. Google Places API (primary) - aggressive pagination + multi-radius
2. Yelp API (optional) - supplementary, captures different listings
3. Yellow Pages (optional) - additional coverage
4. Local directories (optional) - chambers of commerce, local listings

Goal: 95%+ coverage of tree service businesses in each city
"""

import requests
import time
import logging
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedScraper:
    """Multi-source business scraper with maximum coverage"""
    
    def __init__(self, google_api_key: str, yelp_api_key: Optional[str] = None):
        self.google_api_key = google_api_key
        self.yelp_api_key = yelp_api_key
        self.base_url_google = "https://maps.googleapis.com/maps/api/place"
        self.base_url_yelp = "https://api.yelp.com/v3/businesses/search"
        self.timeout = 10
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.rate_limit = 0.5
        self.last_request = 0
        self.all_businesses = {}  # Keyed by normalized identifier to avoid duplicates
    
    def scrape_city_comprehensive(self, city: str, state: str, state_code: str) -> List[Dict]:
        """
        Scrape a city using ALL available sources.
        Returns list of unique businesses found.
        """
        
        logger.info(f"🔍 Starting comprehensive scrape: {city}, {state}")
        
        # Clear previous results
        self.all_businesses = {}
        
        # Source 1: Google Places API (primary, most aggressive)
        logger.info(f"📍 Source 1: Google Places API...")
        google_results = self._scrape_google_places(city, state, state_code)
        self._add_businesses(google_results, "google_places")
        
        # Source 2: Yelp (if API key available)
        if self.yelp_api_key:
            logger.info(f"🍯 Source 2: Yelp API...")
            yelp_results = self._scrape_yelp(city, state)
            self._add_businesses(yelp_results, "yelp")
        
        # Source 3: Yellow Pages (if accessible)
        logger.info(f"📖 Source 3: Yellow Pages...")
        yp_results = self._scrape_yellow_pages(city, state)
        self._add_businesses(yp_results, "yellow_pages")
        
        # Source 4: Local chambers of commerce / directories
        logger.info(f"🏢 Source 4: Local directories...")
        dir_results = self._scrape_local_directories(city, state_code)
        self._add_businesses(dir_results, "local_directory")
        
        results = list(self.all_businesses.values())
        
        logger.info(f"✅ Scrape complete: {len(results)} unique businesses found")
        logger.info(f"   • Google Places: {sum(1 for b in results if b.get('source') == 'google_places')}")
        if self.yelp_api_key:
            logger.info(f"   • Yelp: {sum(1 for b in results if b.get('source') == 'yelp')}")
        logger.info(f"   • Yellow Pages: {sum(1 for b in results if b.get('source') == 'yellow_pages')}")
        logger.info(f"   • Local Directory: {sum(1 for b in results if b.get('source') == 'local_directory')}")
        
        return results
    
    # ====== GOOGLE PLACES (PRIMARY) ======
    
    def _scrape_google_places(self, city: str, state: str, state_code: str) -> List[Dict]:
        """
        Aggressive Google Places scraping:
        - Multiple search term variations (20+)
        - All paginated results
        - Multiple radius searches (1km, 5km, 10km, 25km)
        - Covers city + surrounding area
        """
        
        results = []
        search_terms = self._get_expanded_search_terms()
        
        logger.info(f"Using {len(search_terms)} search term variations...")
        
        for term in search_terms:
            logger.debug(f"  Searching: {term}")
            
            # Strategy 1: Multiple radius searches (covers more area)
            for radius_km in [1, 5, 10, 25]:
                radius_m = radius_km * 1000
                page_results = self._google_places_search(
                    query=f"{term} {city} {state}",
                    location=f"{city}, {state}",
                    radius=radius_m
                )
                results.extend(page_results)
                
                # Rate limiting
                time.sleep(0.2)
            
            time.sleep(0.3)
        
        logger.info(f"Google Places returned {len(results)} results (before dedup)")
        return results
    
    def _get_expanded_search_terms(self) -> List[str]:
        """Extended search terms for maximum coverage"""
        return [
            # Core services
            "tree service",
            "tree removal",
            "tree trimming",
            "tree pruning",
            "arborist",
            "stump grinding",
            "stump removal",
            "land clearing",
            "tree cutting",
            "tree care",
            
            # Variations
            "tree surgeon",
            "forestry service",
            "tree maintenance",
            "tree work",
            "crown reduction",
            "tree felling",
            "wood chipping",
            "brush removal",
            "debris removal",
            "yard cleanup",
            
            # Equipment/specialty
            "tree removal service",
            "professional arborist",
            "certified arborist",
            "emergency tree service",
            "tree emergency",
            "fallen tree removal",
            "storm cleanup",
        ]
    
    def _google_places_search(self, query: str, location: str, radius: int = 50000) -> List[Dict]:
        """Execute Google Places search with pagination"""
        
        results = []
        params = {
            "query": query,
            "key": self.google_api_key,
        }
        
        # Use location if provided
        if location:
            params["location"] = location
            params["radius"] = radius
        
        try:
            url = f"{self.base_url_google}/textsearch/json"
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                logger.debug(f"Google Places status: {data.get('status')}")
                return results
            
            results.extend(data.get("results", []))
            
            # Get ALL pages (aggressive pagination)
            page_token = data.get("next_page_token")
            page_count = 1
            
            while page_token:
                time.sleep(2)  # Google requires 2s between pages
                
                page_params = params.copy()
                page_params["pagetoken"] = page_token
                
                response = requests.get(url, params=page_params, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                
                results.extend(data.get("results", []))
                page_token = data.get("next_page_token")
                page_count += 1
                
                if page_count > 10:  # Safety limit
                    break
        
        except Exception as e:
            logger.warning(f"Google Places search error: {e}")
        
        return results
    
    # ====== YELP (SUPPLEMENTARY) ======
    
    def _scrape_yelp(self, city: str, state: str) -> List[Dict]:
        """Scrape Yelp API for tree service businesses"""
        
        results = []
        
        if not self.yelp_api_key:
            return results
        
        search_terms = [
            "tree service",
            "tree removal",
            "arborist",
            "stump grinding",
            "tree trimming",
        ]
        
        headers = {"Authorization": f"Bearer {self.yelp_api_key}"}
        
        for term in search_terms:
            try:
                params = {
                    "term": term,
                    "location": f"{city}, {state}",
                    "limit": 50,
                    "offset": 0,
                }
                
                response = requests.get(
                    self.base_url_yelp,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                
                for business in data.get("businesses", []):
                    results.append({
                        "place_id": f"yelp_{business['id']}",
                        "business_name": business["name"],
                        "phone": business.get("phone", ""),
                        "address": self._format_address(business.get("location", {})),
                        "rating": business.get("rating"),
                        "review_count": business.get("review_count", 0),
                        "website_url": business.get("url", ""),
                        "city": city,
                        "state": state,
                        "source": "yelp",
                        "category": business.get("categories", []),
                    })
                
                time.sleep(0.5)  # Rate limiting
            
            except Exception as e:
                logger.warning(f"Yelp scrape error: {e}")
        
        logger.info(f"Yelp returned {len(results)} results")
        return results
    
    # ====== YELLOW PAGES ======
    
    def _scrape_yellow_pages(self, city: str, state: str) -> List[Dict]:
        """Scrape Yellow Pages for tree service businesses"""
        
        results = []
        
        # Yellow Pages search URL
        url = f"https://www.yellowpages.com/search"
        
        search_terms = ["tree service", "tree removal", "stump removal"]
        
        for term in search_terms:
            try:
                params = {
                    "search_terms": term,
                    "geo_location_terms": f"{city}, {state}",
                }
                
                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Find business listings
                listings = soup.find_all("div", class_="business-name")
                
                for listing in listings[:20]:  # Limit to first 20 per search
                    try:
                        name_elem = listing.find("a")
                        if not name_elem:
                            continue
                        
                        name = name_elem.get_text(strip=True)
                        
                        # Get phone
                        phone_elem = listing.find_parent().find("div", class_="phone")
                        phone = phone_elem.get_text(strip=True) if phone_elem else ""
                        
                        # Get address
                        addr_elem = listing.find_parent().find("div", class_="address")
                        address = addr_elem.get_text(strip=True) if addr_elem else ""
                        
                        results.append({
                            "place_id": f"yp_{name}_{phone}",
                            "business_name": name,
                            "phone": phone,
                            "address": address,
                            "city": city,
                            "state": state,
                            "source": "yellow_pages",
                        })
                    except Exception as e:
                        logger.debug(f"Yellow Pages parsing error: {e}")
                
                time.sleep(0.5)
            
            except Exception as e:
                logger.warning(f"Yellow Pages scrape error: {e}")
        
        logger.info(f"Yellow Pages returned {len(results)} results")
        return results
    
    # ====== LOCAL DIRECTORIES ======
    
    def _scrape_local_directories(self, city: str, state_code: str) -> List[Dict]:
        """
        Scrape local business directories and chambers of commerce.
        Includes city-specific business listings.
        """
        
        results = []
        
        # This would include:
        # - City chamber of commerce websites
        # - Local business directories
        # - BBB listings
        # - Local gov business registries
        
        # For now, return empty (would need city-specific URLs)
        # In production, you'd have a database of local directories per city
        
        return results
    
    # ====== DEDUPLICATION & CONSOLIDATION ======
    
    def _add_businesses(self, new_businesses: List[Dict], source: str):
        """Add businesses while aggressively deduplicating"""
        
        for business in new_businesses:
            # Generate dedup keys
            keys = self._generate_dedup_keys(business)
            
            # Check if we already have this business
            found_key = None
            for key in keys:
                if key in self.all_businesses:
                    found_key = key
                    break
            
            if found_key:
                # Merge information (keep most complete)
                existing = self.all_businesses[found_key]
                self._merge_business_info(existing, business, source)
            else:
                # New business - add first key as identifier
                primary_key = keys[0] if keys else str(business)
                self.all_businesses[primary_key] = {
                    **business,
                    "sources": [source],
                }
    
    def _generate_dedup_keys(self, business: Dict) -> List[str]:
        """Generate multiple keys for deduplication"""
        keys = []
        
        # Key 1: Phone (most reliable)
        if business.get("phone"):
            phone = self._normalize_phone(business["phone"])
            keys.append(f"phone_{phone}")
        
        # Key 2: Domain (if website available)
        if business.get("website_url"):
            domain = self._extract_domain(business["website_url"])
            if domain:
                keys.append(f"domain_{domain}")
        
        # Key 3: Normalized name + city
        name = self._normalize_name(business.get("business_name", ""))
        city = business.get("city", "").lower()
        if name and city:
            keys.append(f"name_city_{name}_{city}")
        
        # Key 4: Place ID (from source)
        if business.get("place_id"):
            keys.append(f"place_{business['place_id']}")
        
        return keys
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone for comparison"""
        import re
        digits = re.sub(r'\D', '', phone)
        return digits[-10:] if len(digits) >= 10 else digits
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            return domain
        except:
            return None
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        import re
        normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
        return ' '.join(normalized.split())
    
    def _merge_business_info(self, existing: Dict, new: Dict, source: str):
        """Merge information from multiple sources"""
        
        # Track sources
        if "sources" not in existing:
            existing["sources"] = []
        if source not in existing["sources"]:
            existing["sources"].append(source)
        
        # Update fields if new has better data
        if new.get("phone") and not existing.get("phone"):
            existing["phone"] = new["phone"]
        
        if new.get("website_url") and not existing.get("website_url"):
            existing["website_url"] = new["website_url"]
        
        if new.get("rating") and (not existing.get("rating") or new["rating"] > existing["rating"]):
            existing["rating"] = new["rating"]
        
        if new.get("review_count", 0) > existing.get("review_count", 0):
            existing["review_count"] = new["review_count"]
        
        if new.get("address") and not existing.get("address"):
            existing["address"] = new["address"]
    
    def _format_address(self, location: Dict) -> str:
        """Format address from Yelp location data"""
        parts = []
        if location.get("address1"):
            parts.append(location["address1"])
        if location.get("city"):
            parts.append(location["city"])
        if location.get("zip_code"):
            parts.append(location["zip_code"])
        return ", ".join(parts)


def get_enhanced_scraper(google_api_key: str, yelp_api_key: Optional[str] = None) -> EnhancedScraper:
    """Factory function"""
    return EnhancedScraper(google_api_key, yelp_api_key)
