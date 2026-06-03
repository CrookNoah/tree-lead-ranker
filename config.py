from dotenv import load_dotenv
import os
import json

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tree_leads.db")
GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

# Default search terms for tree service businesses
SEARCH_TERMS = [
    "tree service",
    "tree removal",
    "tree trimming",
    "tree cutting",
    "arborist",
    "tree pruning",
    "tree care",
    "tree surgeon",
    "forestry service",
    "tree stump removal",
    "branch removal",
    "tree health care",
    "emergency tree service",
    "tree land clearing",
    "debris removal",
    "wood chipping",
    "tree inspection",
    "tree disease treatment",
    "storm damage cleanup",
    "fallen tree removal"
]

# All US States with major cities
STATES_AND_CITIES = {
    "AL": ["Birmingham", "Montgomery", "Mobile"],
    "AK": ["Anchorage", "Juneau", "Fairbanks"],
    "AZ": ["Phoenix", "Tucson", "Mesa"],
    "AR": ["Little Rock", "Fort Smith", "Fayetteville"],
    "CA": ["Los Angeles", "San Francisco", "San Diego"],
    "CO": ["Denver", "Colorado Springs", "Aurora"],
    "CT": ["Bridgeport", "New Haven", "Hartford"],
    "DE": ["Wilmington", "Dover", "Newark"],
    "FL": ["Miami", "Tampa", "Orlando"],
    "GA": ["Atlanta", "Savannah", "Augusta"],
    "HI": ["Honolulu", "Pearl City", "Kailua"],
    "ID": ["Boise", "Nampa", "Meridian"],
    "IL": ["Chicago", "Springfield", "Peoria"],
    "IN": ["Indianapolis", "Fort Wayne", "Evansville"],
    "IA": ["Des Moines", "Cedar Rapids", "Davenport"],
    "KS": ["Kansas City", "Wichita", "Topeka"],
    "KY": ["Louisville", "Lexington", "Bowling Green"],
    "LA": ["New Orleans", "Baton Rouge", "Shreveport"],
    "ME": ["Portland", "Lewiston", "Auburn"],
    "MD": ["Baltimore", "Annapolis", "Frederick"],
    "MA": ["Boston", "Worcester", "Springfield"],
    "MI": ["Detroit", "Grand Rapids", "Ann Arbor"],
    "MN": ["Minneapolis", "St. Paul", "Rochester"],
    "MS": ["Jackson", "Gulfport", "Biloxi"],
    "MO": ["Kansas City", "St. Louis", "Springfield"],
    "MT": ["Billings", "Missoula", "Great Falls"],
    "NE": ["Omaha", "Lincoln", "Bellevue"],
    "NV": ["Las Vegas", "Henderson", "Reno"],
    "NH": ["Manchester", "Nashua", "Concord"],
    "NJ": ["Newark", "Jersey City", "Paterson"],
    "NM": ["Albuquerque", "Las Cruces", "Santa Fe"],
    "NY": ["New York City", "Buffalo", "Rochester"],
    "NC": ["Charlotte", "Raleigh", "Greensboro"],
    "ND": ["Bismarck", "Grand Forks", "Fargo"],
    "OH": ["Columbus", "Cleveland", "Cincinnati"],
    "OK": ["Oklahoma City", "Tulsa", "Norman"],
    "OR": ["Portland", "Salem", "Eugene"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown"],
    "RI": ["Providence", "Warwick", "Cranston"],
    "SC": ["Charleston", "Columbia", "Greenville"],
    "SD": ["Sioux Falls", "Rapid City", "Aberdeen"],
    "TN": ["Nashville", "Memphis", "Knoxville"],
    "TX": ["Houston", "Dallas", "Austin"],
    "UT": ["Salt Lake City", "Provo", "West Valley City"],
    "VT": ["Burlington", "Rutland", "Barre"],
    "VA": ["Virginia Beach", "Richmond", "Arlington"],
    "WA": ["Seattle", "Spokane", "Tacoma"],
    "WV": ["Charleston", "Huntington", "Parkersburg"],
    "WI": ["Milwaukee", "Madison", "Green Bay"],
    "WY": ["Cheyenne", "Casper", "Laramie"],
}

# Load custom settings from file if exists
SETTINGS_FILE = "settings.json"
def load_settings():
    global STATES_AND_CITIES, SEARCH_TERMS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                if 'states_and_cities' in data:
                    STATES_AND_CITIES = data['states_and_cities']
                if 'search_terms' in data:
                    SEARCH_TERMS = data['search_terms']
        except:
            pass

def save_settings():
    with open(SETTINGS_FILE, 'w') as f:
        json.dump({
            "states_and_cities": STATES_AND_CITIES,
            "search_terms": SEARCH_TERMS
        }, f, indent=2)

load_settings()
