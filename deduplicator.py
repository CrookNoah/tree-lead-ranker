"""Business deduplication logic"""
import re
import logging
from typing import Optional
from urllib.parse import urlparse
from models import Business, SessionLocal

logger = logging.getLogger(__name__)

def extract_domain(url: Optional[str]) -> Optional[str]:
    """Extract domain from URL"""
    if not url:
        return None
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Remove www. prefix
        domain = domain.replace("www.", "")
        return domain
    except Exception:
        return None

def normalize_name(name: str) -> str:
    """Normalize business name for deduplication"""
    # Remove special characters, extra spaces
    normalized = re.sub(r'[^a-z0-9\s]', '', name.lower())
    # Remove extra spaces
    normalized = ' '.join(normalized.split())
    return normalized

def deduplicate_businesses(db: SessionLocal, state: str, city: str):
    """
    Deduplicate businesses in a city by:
    1. Place ID (Google's native dedup)
    2. Phone number
    3. Website domain
    4. Normalized name + city
    """
    
    logger.info(f"Starting deduplication for {city}, {state}")
    
    # Get all non-duplicate businesses for this city
    businesses = db.query(Business).filter(
        Business.state == state,
        Business.city == city,
        Business.is_duplicate == False
    ).all()
    
    logger.info(f"Checking {len(businesses)} businesses for duplicates")
    
    duplicates_found = 0
    
    # Check each business against others
    for i, business in enumerate(businesses):
        if business.is_duplicate:
            continue  # Skip if already marked
        
        # Find potential duplicates
        potential_dupes = businesses[i+1:]
        
        for other in potential_dupes:
            if other.is_duplicate:
                continue
            
            is_duplicate = False
            reason = ""
            
            # Check 1: Same place ID (shouldn't happen, but just in case)
            if business.place_id == other.place_id:
                is_duplicate = True
                reason = "Same Google Place ID"
            
            # Check 2: Same phone number
            elif (business.phone and other.phone and 
                  normalize_phone(business.phone) == normalize_phone(other.phone)):
                is_duplicate = True
                reason = "Same phone number"
            
            # Check 3: Same domain
            elif (business.domain and other.domain and 
                  business.domain == other.domain):
                is_duplicate = True
                reason = "Same website domain"
            
            # Check 4: Similar name + same city (fuzzy match)
            elif (business.normalized_name == other.normalized_name and
                  business.city == other.city):
                is_duplicate = True
                reason = "Same normalized name + city"
            
            # Mark the duplicate (keep the one with more reviews)
            if is_duplicate:
                if other.review_count >= business.review_count:
                    # Keep other, mark business as duplicate
                    business.is_duplicate = True
                    business.duplicate_of_id = other.id
                    logger.info(f"Marked {business.business_name} as duplicate of {other.business_name} ({reason})")
                    duplicates_found += 1
                    break
                else:
                    # Keep business, mark other as duplicate
                    other.is_duplicate = True
                    other.duplicate_of_id = business.id
                    logger.info(f"Marked {other.business_name} as duplicate of {business.business_name} ({reason})")
                    duplicates_found += 1
    
    db.commit()
    logger.info(f"Deduplication complete: {duplicates_found} duplicates found")

def normalize_phone(phone: str) -> str:
    """Normalize phone number for comparison"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    # Return last 10 digits (US phone number)
    return digits[-10:] if len(digits) >= 10 else digits
