"""Database models for Tree Lead Ranker"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL

Base = declarative_base()

class Business(Base):
    __tablename__ = "businesses"
    
    id = Column(Integer, primary_key=True)
    place_id = Column(String, unique=True, index=True)
    business_name = Column(String, index=True)
    phone = Column(String, index=True)
    address = Column(String)
    city = Column(String, index=True)
    state = Column(String)
    category = Column(String)
    rating = Column(Float)
    review_count = Column(Integer)
    website_url = Column(String)
    google_listing_url = Column(String)
    source = Column(String)  # "google_places"
    
    # Deduplication fields
    normalized_name = Column(String, index=True)
    domain = Column(String)
    
    # Website audit
    website_status = Column(String)  # no_website, broken, facebook_only, working
    website_reachable = Column(Boolean)
    https = Column(Boolean)
    mobile_viewport = Column(Boolean)
    phone_visible = Column(Boolean)
    click_to_call = Column(Boolean)
    contact_form = Column(Boolean)
    quote_cta = Column(Boolean)
    service_pages = Column(Boolean)
    location_pages = Column(Boolean)
    reviews_testimonials = Column(Boolean)
    before_after_gallery = Column(Boolean)
    title_tag = Column(String)
    meta_description = Column(String)
    outdated_design = Column(Boolean)
    
    # Scoring
    website_quality_score = Column(Float)  # 0-100
    website_grade = Column(String)  # A, B, C, D, F, Broken, No Website
    
    # Behavioral Scoring (Activity-based, more predictive than website quality alone)
    activity_score = Column(Float)  # 0-100: How active/engaged is the business?
    activity_breakdown = Column(JSON)  # Detailed breakdown: recent_reviews, sentiment_trend, etc.
    readiness = Column(String)  # HOT, WARM, COLD, FROZEN
    readiness_recommendation = Column(String)  # Specific advice based on activity
    
    # AI Analysis
    lead_type = Column(String)
    call_priority = Column(String)  # Call Now, Maybe Later, Skip
    recommended_offer = Column(String)
    main_problem = Column(String)
    why_this_lead_matters = Column(String)
    cold_call_opener = Column(String)
    short_pitch = Column(String)
    follow_up_sms = Column(String)
    follow_up_email = Column(String)
    crm_note = Column(String)
    sales_opportunity_score = Column(Float)  # 0-100
    
    # Decision-Maker Intelligence
    primary_contact_name = Column(String)
    primary_contact_role = Column(String)
    primary_contact_phone = Column(String)
    primary_contact_email = Column(String)
    secondary_contacts = Column(JSON)  # List of backup contacts
    contact_confidence = Column(Float)  # 0-100: How confident we are about contact accuracy
    
    # Financial ROI
    estimated_monthly_jobs = Column(Float)
    estimated_job_value = Column(Float)
    estimated_monthly_revenue = Column(Float)
    estimated_annual_revenue = Column(Float)
    estimated_lost_revenue_monthly = Column(Float)  # From poor online presence
    estimated_lost_revenue_yearly = Column(Float)
    potential_revenue_increase = Column(Float)  # Annual upside from improvement
    roi_payback_months = Column(Float)  # How long to recoup investment
    roi_percentage = Column(Float)  # Year 1 ROI
    roi_pitch = Column(String)  # Data-driven pitch
    
    # Outreach Tracking
    sms_sent = Column(Boolean, default=False)
    sms_sent_at = Column(DateTime)
    sms_message = Column(String)
    emails_sent = Column(Integer, default=0)  # Number of emails in sequence
    first_email_sent_at = Column(DateTime)
    opted_out_sms = Column(Boolean, default=False)
    opted_out_email = Column(Boolean, default=False)
    
    # Call Tracking
    call_logged = Column(Boolean, default=False)
    call_outcome = Column(String)  # not-interested, call-back, interested, meeting-set, closed
    call_notes = Column(String)  # Notes from call
    call_date = Column(DateTime)  # When the call was made
    call_duration = Column(Integer)  # Duration in seconds
    
    # Lead Tags
    tags = Column(JSON)  # List of tags: ["hot-prospect", "vip", "follow-up"]
    
    # Metadata
    date_added = Column(DateTime, default=datetime.utcnow)
    date_scanned = Column(DateTime, default=datetime.utcnow)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer)  # Reference to primary business ID
    audit_log = Column(JSON)  # Store audit findings


# Create engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
