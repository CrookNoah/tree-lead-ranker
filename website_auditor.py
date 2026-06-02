"""Website auditing and quality scoring"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class WebsiteAuditor:
    def __init__(self):
        self.timeout = 10
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def check_website_status(self, url: str) -> Tuple[str, bool]:
        """
        Check if website is reachable and working
        Returns: (status, is_reachable)
        status: no_website, broken, facebook_only, working
        """
        if not url or url.strip() == "":
            return "no_website", False
        
        # Clean URL
        url = url.strip()
        if not url.startswith("http"):
            url = f"https://{url}"
        
        try:
            response = requests.head(url, timeout=self.timeout, headers=self.headers, allow_redirects=True)
            
            # Check for redirects to Facebook/directory sites
            if "facebook.com" in response.url.lower() or "yelp.com" in response.url.lower():
                return "facebook_only", False
            
            if response.status_code < 400:
                return "working", True
            elif response.status_code < 500:
                return "broken", False
            else:
                return "broken", False
        
        except requests.Timeout:
            return "broken", False
        except requests.ConnectionError:
            return "broken", False
        except Exception as e:
            logger.warning(f"Website check error for {url}: {e}")
            return "broken", False
    
    def fetch_page(self, url: str) -> Tuple[str, bool]:
        """Fetch website content"""
        if not url.startswith("http"):
            url = f"https://{url}"
        
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers, allow_redirects=True)
            if response.status_code == 200:
                return response.text, True
            return "", False
        except Exception as e:
            logger.warning(f"Error fetching {url}: {e}")
            return "", False
    
    def audit_website(self, url: str) -> Dict:
        """Comprehensive website audit"""
        audit = {
            "website_reachable": False,
            "https": False,
            "mobile_viewport": False,
            "phone_visible": False,
            "click_to_call": False,
            "contact_form": False,
            "quote_cta": False,
            "service_pages": False,
            "location_pages": False,
            "reviews_testimonials": False,
            "before_after_gallery": False,
            "title_tag": "",
            "meta_description": "",
            "outdated_design": False,
        }
        
        if not url:
            return audit
        
        # Check HTTPS
        audit["https"] = url.startswith("https")
        
        # Fetch page
        html, success = self.fetch_page(url)
        if not success:
            return audit
        
        audit["website_reachable"] = True
        
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            # Mobile viewport
            viewport = soup.find("meta", attrs={"name": "viewport"})
            audit["mobile_viewport"] = viewport is not None
            
            # Title and meta
            title = soup.find("title")
            audit["title_tag"] = title.string if title else ""
            
            meta_desc = soup.find("meta", attrs={"name": "description"})
            audit["meta_description"] = meta_desc.get("content", "") if meta_desc else ""
            
            # Phone number patterns
            phone_pattern = r'\(?[\d\s\-\+\(\)]{7,}\)?'
            text = soup.get_text()
            has_phone = bool(re.search(phone_pattern, text))
            audit["phone_visible"] = has_phone
            
            # Click to call
            tel_links = soup.find_all("a", href=re.compile(r"^tel:"))
            audit["click_to_call"] = len(tel_links) > 0
            
            # Contact form
            forms = soup.find_all("form")
            has_contact_form = any(
                "contact" in str(form).lower() or "message" in str(form).lower()
                for form in forms
            )
            audit["contact_form"] = has_contact_form
            
            # Quote/estimate CTA
            page_text = text.lower()
            quote_keywords = ["free estimate", "free quote", "request quote", "get quote", "free assessment"]
            audit["quote_cta"] = any(kw in page_text for kw in quote_keywords)
            
            # Service pages
            links = [a.get("href", "") for a in soup.find_all("a")]
            service_keywords = ["service", "tree removal", "trimming", "stump", "services"]
            has_service_pages = any(
                any(kw in link.lower() for kw in service_keywords)
                for link in links if link
            )
            audit["service_pages"] = has_service_pages
            
            # Location pages
            location_keywords = ["service area", "areas served", "coverage", "serve"]
            has_location_pages = any(
                any(kw in link.lower() for kw in location_keywords)
                for link in links if link
            )
            audit["location_pages"] = has_location_pages
            
            # Reviews/testimonials
            review_keywords = ["review", "testimonial", "customer review", "5 star"]
            audit["reviews_testimonials"] = any(kw in page_text for kw in review_keywords)
            
            # Before/after gallery
            imgs = soup.find_all("img")
            audit["before_after_gallery"] = any(
                "before" in str(img).lower() or "after" in str(img).lower()
                for img in imgs
            )
            
            # Outdated design signals
            outdated_signals = [
                soup.find("marquee"),  # Very old HTML
                soup.find("blink"),    # Very old HTML
                len(soup.find_all("table")) > 10,  # Table layouts
                "jQuery" in html and "2000" in html,  # Ancient jQuery
                re.search(r"(design|built|created) in (200\d|201\d)", html, re.I),
            ]
            audit["outdated_design"] = any(outdated_signals)
        
        except Exception as e:
            logger.warning(f"Error parsing {url}: {e}")
        
        return audit
    
    def calculate_quality_score(self, audit: Dict) -> float:
        """Score website quality 0-100"""
        score = 0
        
        if not audit["website_reachable"]:
            return 0
        
        # Points for each audit item
        weights = {
            "https": 10,
            "mobile_viewport": 10,
            "phone_visible": 15,
            "click_to_call": 10,
            "contact_form": 15,
            "quote_cta": 20,
            "service_pages": 10,
            "location_pages": 5,
            "reviews_testimonials": 10,
            "before_after_gallery": 5,
        }
        
        for item, weight in weights.items():
            if audit.get(item, False):
                score += weight
        
        # Penalty for outdated design
        if audit.get("outdated_design", False):
            score = max(0, score - 15)
        
        return min(100, score)
    
    def grade_website(self, score: float, status: str) -> str:
        """Convert score to letter grade"""
        if status == "no_website":
            return "No Website"
        elif status == "broken":
            return "Broken Website"
        elif score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


def get_auditor() -> WebsiteAuditor:
    return WebsiteAuditor()
