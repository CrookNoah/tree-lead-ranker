"""Tree Lead Ranker - FastAPI Backend"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime
import csv
from io import StringIO

from models import Business, SessionLocal
from places_api import get_places_api
from website_auditor import get_auditor
from lead_analyzer import get_analyzer
from behavioral_scorer import get_behavioral_scorer
from decision_maker_finder import get_decision_maker_finder
from roi_calculator import get_roi_calculator
from deduplicator import deduplicate_businesses, extract_domain, normalize_name
from config import STATES_AND_CITIES

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tree Lead Ranker")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class ScanRequest(BaseModel):
    state: str
    city: str

class LeadFilter(BaseModel):
    state: Optional[str] = None
    city: Optional[str] = None
    website_grade: Optional[str] = None
    min_reviews: Optional[int] = None
    call_priority: Optional[str] = None

# Routes

@app.get("/dashboard_v2.html", response_class=None)
def get_dashboard_v2():
    """Serve dashboard v2"""
    from fastapi.responses import FileResponse
    import os
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard_v2.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Dashboard not found")

@app.get("/dashboard.html", response_class=None)
def get_dashboard():
    """Serve dashboard v1"""
    from fastapi.responses import FileResponse
    import os
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    if os.path.exists(dashboard_path):
        return FileResponse(dashboard_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Dashboard not found")

@app.get("/")
def read_root():
    return {"message": "Tree Lead Ranker API"}

@app.get("/states")
def get_states():
    """Get list of states and their cities"""
    return STATES_AND_CITIES

@app.get("/states/{state_code}/cities")
def get_cities(state_code: str):
    """Get cities for a state"""
    if state_code not in STATES_AND_CITIES:
        raise HTTPException(status_code=404, detail="State not found")
    
    state_data = STATES_AND_CITIES[state_code]
    return {
        "state_code": state_code,
        "state_name": state_data["state_name"],
        "cities": state_data["cities"]
    }

@app.post("/scan")
async def scan_city(request: ScanRequest, background_tasks: BackgroundTasks):
    """Scan a city for tree service businesses"""
    
    if request.state not in STATES_AND_CITIES:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    state_data = STATES_AND_CITIES[request.state]
    if request.city not in state_data["cities"]:
        raise HTTPException(status_code=400, detail="Invalid city for state")
    
    # Start scan in background
    background_tasks.add_task(
        perform_scan,
        request.state,
        request.city,
        state_data["state_name"]
    )
    
    return {"status": "Scanning started", "state": request.state, "city": request.city}

def perform_scan(state_code: str, city: str, state_name: str):
    """Perform the actual scan and database update"""
    logger.info(f"Starting scan for {city}, {state_name}")
    
    db = SessionLocal()
    try:
        # Step 1: Search for businesses
        places_api = get_places_api()
        businesses = places_api.search_city(city, state_name, state_code)
        logger.info(f"Found {len(businesses)} businesses")
        
        # Step 2: Save to database
        auditor = get_auditor()
        analyzer = get_analyzer()
        behavioral_scorer = get_behavioral_scorer()
        decision_maker_finder = get_decision_maker_finder()
        roi_calc = get_roi_calculator()
        
        for business_data in businesses:
            # Check for duplicates
            existing = db.query(Business).filter(
                Business.place_id == business_data["place_id"]
            ).first()
            
            if existing:
                logger.debug(f"Business {business_data['business_name']} already exists")
                continue
            
            # Create business record
            business = Business(
                place_id=business_data["place_id"],
                business_name=business_data["business_name"],
                phone=business_data["phone"],
                address=business_data["address"],
                city=business_data["city"],
                state=business_data["state"],
                category=str(business_data.get("category", [])),
                rating=business_data.get("rating"),
                review_count=business_data.get("review_count", 0),
                website_url=business_data.get("website_url"),
                google_listing_url=business_data.get("google_listing_url"),
                source="google_places",
                normalized_name=normalize_name(business_data["business_name"]),
                domain=extract_domain(business_data.get("website_url")),
            )
            
            # Stage 3: Audit website
            if business_data.get("website_url"):
                audit = auditor.audit_website(business_data["website_url"])
                business.website_reachable = audit["website_reachable"]
                business.https = audit["https"]
                business.mobile_viewport = audit["mobile_viewport"]
                business.phone_visible = audit["phone_visible"]
                business.click_to_call = audit["click_to_call"]
                business.contact_form = audit["contact_form"]
                business.quote_cta = audit["quote_cta"]
                business.service_pages = audit["service_pages"]
                business.location_pages = audit["location_pages"]
                business.reviews_testimonials = audit["reviews_testimonials"]
                business.before_after_gallery = audit["before_after_gallery"]
                business.title_tag = audit["title_tag"]
                business.meta_description = audit["meta_description"]
                business.outdated_design = audit["outdated_design"]
                
                # Stage 4: Score and grade
                website_status, reachable = auditor.check_website_status(business_data["website_url"])
                business.website_status = website_status
                business.website_reachable = reachable
                
                if website_status == "working":
                    score = auditor.calculate_quality_score(audit)
                    business.website_quality_score = score
                    business.website_grade = auditor.grade_website(score, website_status)
                else:
                    business.website_quality_score = 0
                    business.website_grade = auditor.grade_website(0, website_status)
            else:
                business.website_status = "no_website"
                business.website_quality_score = 0
                business.website_grade = "No Website"
            
            # Stage 4.5: Behavioral Scoring (Activity-based readiness)
            behavioral = behavioral_scorer.score_behavior(business.__dict__)
            business.activity_score = behavioral["activity_score"]
            business.activity_breakdown = behavioral["breakdown"]
            business.readiness = behavioral["readiness"]
            business.readiness_recommendation = behavioral["recommendation"]
            logger.info(f"Behavioral score for {business.business_name}: {behavioral['activity_score']}/100 ({behavioral['readiness']})")
            
            # Stage 4.75: Decision-Maker Intelligence
            decision_makers = decision_maker_finder.find_decision_makers(business.__dict__)
            if decision_makers["primary_contact"]:
                primary = decision_makers["primary_contact"]
                business.primary_contact_name = primary.get("name")
                business.primary_contact_role = primary.get("role")
                business.primary_contact_phone = primary.get("phone")
                business.primary_contact_email = primary.get("email")
                business.contact_confidence = primary.get("confidence", 0)
                business.secondary_contacts = decision_makers["secondary_contacts"]
                logger.info(f"Found primary contact: {primary.get('name')} ({primary.get('role')})")
            
            # Stage 4.9: ROI Calculator
            roi = roi_calc.calculate_roi(business.__dict__)
            current = roi["current_state"]
            business.estimated_monthly_jobs = current["monthly_jobs"]
            business.estimated_job_value = current["job_value"]
            business.estimated_monthly_revenue = current["monthly_revenue"]
            business.estimated_annual_revenue = current["annual_revenue"]
            business.estimated_lost_revenue_monthly = current["estimated_lost_revenue_monthly"]
            business.estimated_lost_revenue_yearly = current["estimated_lost_revenue_yearly"]
            
            recommendation = roi["recommended_offer"]
            business.potential_revenue_increase = recommendation["annual_revenue_impact"]
            business.roi_payback_months = recommendation["payback_period_months"]
            business.roi_percentage = recommendation["roi_percentage"]
            business.roi_pitch = roi["pitch"]
            logger.info(f"ROI analysis: ${recommendation['annual_revenue_impact']}/year upside, {recommendation['payback_period_months']} month payback")
            
            # Stage 5: AI Analysis
            analysis = analyzer.analyze_lead(business.__dict__)
            business.lead_type = analysis.get("lead_type")
            business.call_priority = analysis.get("call_priority")
            business.recommended_offer = analysis.get("recommended_offer")
            business.main_problem = analysis.get("main_problem")
            business.why_this_lead_matters = analysis.get("why_this_lead_matters")
            business.cold_call_opener = analysis.get("cold_call_opener")
            business.short_pitch = analysis.get("short_pitch")
            business.follow_up_sms = analysis.get("follow_up_sms")
            business.follow_up_email = analysis.get("follow_up_email")
            business.crm_note = analysis.get("crm_note")
            business.sales_opportunity_score = analysis.get("sales_opportunity_score", 0)
            
            business.date_scanned = datetime.utcnow()
            
            db.add(business)
            db.commit()
            
            logger.info(f"Added: {business.business_name} - {business.call_priority}")
        
        # Step 2b: Deduplicate
        deduplicate_businesses(db, state_code, city)
        
        logger.info(f"Scan complete for {city}, {state_name}")
    
    except Exception as e:
        logger.error(f"Scan error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

@app.get("/leads")
def get_leads(filters: Optional[str] = None):
    """Get leads with optional filtering"""
    db = SessionLocal()
    try:
        query = db.query(Business).filter(Business.is_duplicate == False)
        
        # Apply filters if provided
        # TODO: Parse filter string and apply
        
        leads = query.all()
        return [serialize_business(b) for b in leads]
    finally:
        db.close()

@app.get("/leads/{lead_id}")
def get_lead(lead_id: int):
    """Get single lead"""
    db = SessionLocal()
    try:
        lead = db.query(Business).filter(Business.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return serialize_business(lead)
    finally:
        db.close()

@app.get("/export/csv")
def export_csv(state: Optional[str] = None):
    """Export leads as CSV"""
    db = SessionLocal()
    try:
        query = db.query(Business).filter(Business.is_duplicate == False)
        
        if state:
            query = query.filter(Business.state == state)
        
        leads = query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "business_name", "phone", "address", "city", "state",
            "rating", "review_count", "website_url", "website_grade",
            "website_quality_score", "sales_opportunity_score",
            "lead_type", "call_priority", "recommended_offer",
            "main_problem", "cold_call_opener", "follow_up_sms",
            "follow_up_email", "crm_note", "date_scanned"
        ])
        
        writer.writeheader()
        for lead in leads:
            writer.writerow({
                "business_name": lead.business_name,
                "phone": lead.phone,
                "address": lead.address,
                "city": lead.city,
                "state": lead.state,
                "rating": lead.rating,
                "review_count": lead.review_count,
                "website_url": lead.website_url,
                "website_grade": lead.website_grade,
                "website_quality_score": lead.website_quality_score,
                "sales_opportunity_score": lead.sales_opportunity_score,
                "lead_type": lead.lead_type,
                "call_priority": lead.call_priority,
                "recommended_offer": lead.recommended_offer,
                "main_problem": lead.main_problem,
                "cold_call_opener": lead.cold_call_opener,
                "follow_up_sms": lead.follow_up_sms,
                "follow_up_email": lead.follow_up_email,
                "crm_note": lead.crm_note,
                "date_scanned": lead.date_scanned.isoformat() if lead.date_scanned else ""
            })
        
        return {
            "csv": output.getvalue(),
            "filename": f"tree_leads_{state or 'all'}.csv"
        }
    finally:
        db.close()

@app.get("/stats")
def get_stats():
    """Get scan statistics"""
    db = SessionLocal()
    try:
        total = db.query(Business).filter(Business.is_duplicate == False).count()
        call_now = db.query(Business).filter(
            Business.is_duplicate == False,
            Business.call_priority == "Call Now"
        ).count()
        no_website = db.query(Business).filter(
            Business.is_duplicate == False,
            Business.website_status == "no_website"
        ).count()
        called = db.query(Business).filter(
            Business.is_duplicate == False,
            Business.call_logged == True
        ).count()
        closed = db.query(Business).filter(
            Business.is_duplicate == False,
            Business.call_outcome == "closed"
        ).count()
        
        return {
            "total_leads": total,
            "call_now": call_now,
            "no_website": no_website,
            "called": called,
            "closed": closed,
        }
    finally:
        db.close()

@app.post("/leads/{lead_id}/call-log")
def log_call(lead_id: int, outcome: str, notes: str = ""):
    """Log a call for a lead"""
    db = SessionLocal()
    try:
        lead = db.query(Business).filter(Business.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        lead.call_logged = True
        lead.call_outcome = outcome
        lead.call_notes = notes
        lead.call_date = datetime.utcnow()
        
        db.commit()
        logger.info(f"Call logged for {lead.business_name}: {outcome}")
        
        return {"success": True, "message": "Call logged"}
    except Exception as e:
        db.rollback()
        logger.error(f"Call log error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@app.post("/leads/{lead_id}/tag")
def add_tag(lead_id: int, tag: str):
    """Add a tag to a lead"""
    db = SessionLocal()
    try:
        lead = db.query(Business).filter(Business.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        if not lead.tags:
            lead.tags = []
        
        if tag not in lead.tags:
            lead.tags.append(tag)
        
        db.commit()
        logger.info(f"Tag '{tag}' added to {lead.business_name}")
        
        return {"success": True, "message": f"Tag added", "tags": lead.tags}
    except Exception as e:
        db.rollback()
        logger.error(f"Tag error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

# Settings endpoints
@app.get("/settings")
def get_settings():
    """Get current settings"""
    return {"states_and_cities": STATES_AND_CITIES}

class SettingsUpdate(BaseModel):
    states_and_cities: dict

@app.post("/settings/update")
def update_settings(settings: SettingsUpdate):
    """Update states and cities configuration"""
    from config import save_settings
    global STATES_AND_CITIES
    
    try:
        STATES_AND_CITIES = settings.states_and_cities
        save_settings()
        logger.info("Settings updated")
        return {"success": True, "message": "Settings updated", "states_and_cities": STATES_AND_CITIES}
    except Exception as e:
        logger.error(f"Settings update error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

def serialize_business(business: Business) -> dict:
    """Convert Business model to dict"""
    return {
        "id": business.id,
        "business_name": business.business_name,
        "phone": business.phone,
        "address": business.address,
        "city": business.city,
        "state": business.state,
        "rating": business.rating,
        "review_count": business.review_count,
        "website_url": business.website_url,
        "website_grade": business.website_grade,
        "website_quality_score": business.website_quality_score,
        "website_status": business.website_status,
        "sales_opportunity_score": business.sales_opportunity_score,
        "lead_type": business.lead_type,
        "call_priority": business.call_priority,
        "recommended_offer": business.recommended_offer,
        "main_problem": business.main_problem,
        "why_this_lead_matters": business.why_this_lead_matters,
        "cold_call_opener": business.cold_call_opener,
        "short_pitch": business.short_pitch,
        "follow_up_sms": business.follow_up_sms,
        "follow_up_email": business.follow_up_email,
        "crm_note": business.crm_note,
        "date_scanned": business.date_scanned.isoformat() if business.date_scanned else "",
        "activity_score": business.activity_score,
        "readiness": business.readiness,
        "readiness_recommendation": business.readiness_recommendation,
        "activity_breakdown": business.activity_breakdown,
        "primary_contact_name": business.primary_contact_name,
        "primary_contact_role": business.primary_contact_role,
        "primary_contact_phone": business.primary_contact_phone,
        "primary_contact_email": business.primary_contact_email,
        "contact_confidence": business.contact_confidence,
        "secondary_contacts": business.secondary_contacts,
        "estimated_monthly_jobs": business.estimated_monthly_jobs,
        "estimated_job_value": business.estimated_job_value,
        "estimated_monthly_revenue": business.estimated_monthly_revenue,
        "estimated_annual_revenue": business.estimated_annual_revenue,
        "estimated_lost_revenue_monthly": business.estimated_lost_revenue_monthly,
        "estimated_lost_revenue_yearly": business.estimated_lost_revenue_yearly,
        "potential_revenue_increase": business.potential_revenue_increase,
        "roi_payback_months": business.roi_payback_months,
        "roi_percentage": business.roi_percentage,
        "roi_pitch": business.roi_pitch,
        "sms_sent": business.sms_sent,
        "emails_sent": business.emails_sent,
        "call_logged": business.call_logged,
        "call_outcome": business.call_outcome,
        "call_notes": business.call_notes,
        "call_date": business.call_date.isoformat() if business.call_date else None,
        "tags": business.tags or [],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
