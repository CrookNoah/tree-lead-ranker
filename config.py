"""Configuration for Tree Lead Ranker"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Database
DATABASE_URL = "sqlite:///./tree_leads.db"

# Search terms for tree services
SEARCH_TERMS = [
    "tree service",
    "tree removal",
    "tree trimming",
    "arborist",
    "stump grinding",
    "land clearing",
]

# US States with their major cities (sample)
STATES_AND_CITIES = {
    "SC": {
        "state_name": "South Carolina",
        "cities": [
            "Charleston",
            "Columbia",
            "Greenville",
            "Spartanburg",
            "Summerville",
            "Hilton Head",
            "Florence",
            "Anderson",
            "Beaufort",
            "Myrtle Beach",
            "Goose Creek",
            "Aiken",
            "Laurens",
            "Easley",
            "Clemson",
            "Orangeburg",
            "Walterboro",
            "Georgetown",
            "Barnwell",
            "Sumter",
        ]
    },
    "NC": {
        "state_name": "North Carolina",
        "cities": [
            "Charlotte",
            "Raleigh",
            "Greensboro",
            "Durham",
            "Chapel Hill",
            "Wilmington",
            "High Point",
            "Fayetteville",
            "Cary",
            "Winston-Salem",
        ]
    },
    "GA": {
        "state_name": "Georgia",
        "cities": [
            "Atlanta",
            "Savannah",
            "Augusta",
            "Athens",
            "Marietta",
            "Alpharetta",
            "Decatur",
            "Roswell",
        ]
    },
}

# Website audit checklist
WEBSITE_AUDIT_ITEMS = [
    "https",
    "mobile_viewport",
    "phone_visible",
    "click_to_call",
    "contact_form",
    "quote_cta",
    "service_pages",
    "location_pages",
    "reviews_testimonials",
    "before_after_gallery",
    "title_tag",
    "meta_description",
    "outdated_design",
]

# AI Model preference
AI_MODEL = "anthropic"  # or "openai"
