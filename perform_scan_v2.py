"""Simplified scan function that actually works"""
import logging
from datetime import datetime
from models import Business, SessionLocal
from places_api import get_places_api
from state_names import get_state_name
from deduplicator import deduplicate_businesses, extract_domain, normalize_name
from config import GOOGLE_PLACES_API_KEY

logger = logging.getLogger(__name__)

def perform_scan_simple(state_code: str, city: str, scan_progress: dict):
    """Simple scan that JUST saves leads from Places API"""
    
    state_name = get_state_name(state_code)
    logger.info(f"\n\n{'='*70}")
    logger.info(f"🚀 SCAN STARTED: {city}, {state_name} ({state_code})")
    logger.info(f"{'='*70}")
    
    # Set scanning state
    scan_progress["scanning"] = True
    scan_progress["state"] = state_code
    scan_progress["city"] = city
    scan_progress["found"] = 0
    scan_progress["processed"] = 0
    scan_progress["leads"] = []
    scan_progress["status_message"] = "Searching Google Places..."
    
    if not GOOGLE_PLACES_API_KEY:
        error_msg = "❌ GOOGLE_PLACES_API_KEY not set!"
        logger.error(error_msg)
        scan_progress["status_message"] = error_msg
        scan_progress["scanning"] = False
        return
    
    db = SessionLocal()
    try:
        # Step 1: Get businesses from Google Places API
        logger.info("🔍 Calling Google Places API...")
        places_api = get_places_api()
        businesses = places_api.search_city(city, state_name, state_code)
        
        logger.info(f"✅ API returned {len(businesses)} results")
        
        if len(businesses) == 0:
            logger.warning("⚠️ No businesses found!")
            scan_progress["status_message"] = "No businesses found"
            scan_progress["scanning"] = False
            return
        
        # Update found count
        scan_progress["found"] = len(businesses)
        scan_progress["status_message"] = f"Found {len(businesses)} businesses, saving to database..."
        logger.info(f"📊 Status: {scan_progress['status_message']}")
        
        # Step 2: Save each business to database
        saved_count = 0
        for idx, business_data in enumerate(businesses):
            try:
                # Update progress
                scan_progress["processed"] = idx + 1
                scan_progress["status_message"] = f"Saving {idx + 1}/{len(businesses)}: {business_data.get('business_name', '?')}"
                logger.debug(f"[{idx+1}/{len(businesses)}] {business_data.get('business_name')}")
                
                # Check if already exists
                existing = db.query(Business).filter(
                    Business.place_id == business_data.get("place_id")
                ).first()
                
                if existing:
                    logger.debug(f"  ↻ Already exists, skipping")
                    continue
                
                # Create basic business record
                business = Business(
                    place_id=business_data.get("place_id"),
                    business_name=business_data.get("business_name", "Unknown"),
                    phone=business_data.get("phone", ""),
                    address=business_data.get("address", ""),
                    city=city,
                    state=state_code,
                    category=str(business_data.get("category", [])),
                    rating=business_data.get("rating"),
                    review_count=business_data.get("review_count", 0),
                    website_url=business_data.get("website_url", ""),
                    google_listing_url=business_data.get("google_listing_url", ""),
                    source="google_places",
                    normalized_name=normalize_name(business_data.get("business_name", "Unknown")),
                    domain=extract_domain(business_data.get("website_url", "")),
                    date_scanned=datetime.utcnow(),
                    call_priority="medium",
                    website_grade="Not Analyzed",
                    activity_score=50,
                )
                
                # Save to database
                db.add(business)
                db.commit()
                saved_count += 1
                logger.info(f"  ✅ Saved: {business.business_name}")
                
                # Add to real-time progress
                lead_summary = {
                    "id": business.id,
                    "business_name": business.business_name,
                    "city": business.city,
                    "phone": business.phone,
                    "website_grade": business.website_grade,
                    "activity_score": business.activity_score,
                    "call_priority": business.call_priority
                }
                scan_progress["leads"].append(lead_summary)
                
            except Exception as e:
                logger.error(f"  ❌ Error saving business: {str(e)}", exc_info=True)
                db.rollback()
                continue
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ SCAN COMPLETE: {city}, {state_name}")
        logger.info(f"📊 Saved {saved_count}/{len(businesses)} leads")
        logger.info(f"{'='*70}\n")
        
        scan_progress["status_message"] = f"✅ Complete! Saved {saved_count} leads"
        
    except Exception as e:
        logger.error(f"❌ SCAN ERROR: {str(e)}", exc_info=True)
        scan_progress["status_message"] = f"Error: {str(e)}"
        db.rollback()
    finally:
        scan_progress["scanning"] = False
        db.close()
