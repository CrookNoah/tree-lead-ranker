"""AI-powered lead analysis"""
import json
import logging
from typing import Dict
from config import AI_MODEL, OPENAI_API_KEY, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

class LeadAnalyzer:
    def __init__(self, model: str = "anthropic"):
        self.model = model
        if model == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
        elif model == "openai":
            from openai import OpenAI
            self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def analyze_lead(self, business: Dict) -> Dict:
        """AI analysis of a business for sales opportunity"""
        
        # Include behavioral scoring in context
        activity_score = business.get('activity_score', 0)
        readiness = business.get('readiness', 'UNKNOWN')
        
        # Build context from business data
        context = f"""
Business: {business['business_name']}
Location: {business['city']}, {business['state']}
Phone: {business['phone']}
Website: {business['website_url'] or 'No website'}
Google Rating: {business['rating']}/5 ({business['review_count']} reviews)
Website Grade: {business['website_grade']}
Website Quality Score: {business['website_quality_score']}/100
Current Website Status: {business['website_status']}

BEHAVIORAL SIGNALS (Activity/Readiness):
Activity Score: {activity_score}/100
Readiness Level: {readiness}
This business is {readiness} for investment based on current activity signals.

Website Features:
- HTTPS: {business['https']}
- Mobile Responsive: {business['mobile_viewport']}
- Phone Visible: {business['phone_visible']}
- Click-to-Call: {business['click_to_call']}
- Contact Form: {business['contact_form']}
- Quote/Estimate CTA: {business['quote_cta']}
- Service Pages: {business['service_pages']}
- Location Pages: {business['location_pages']}
- Reviews/Testimonials: {business['reviews_testimonials']}
- Before/After Gallery: {business['before_after_gallery']}

Analyze this tree service business for my digital marketing services. I offer:
1. No website: $500 starter website + $99/month hosting/support
2. Broken website: $700 repair/rebuild + $99/month hosting/support
3. Bad website: $700 redesign + $99/month hosting/support
4. Decent website: Local SEO, HighLevel CRM, missed-call texting, review automation
5. Good website: Advanced marketing, CRM automation, retargeting, landing pages

PRIORITY RULES (use these for call_priority):
- Activity 75+ + any website problem = "Call Now" (they're busy, have budget)
- Activity 75+ + good website = "Call Now" (opportunity for advanced marketing)
- Activity 55-74 + no/broken website = "Call Now" (obvious pain point, mid-tier activity)
- Activity 55-74 + bad website = "Maybe Later" (can work but lower urgency)
- Activity <55 = "Maybe Later" or "Skip" (low activity = low intent)
- Bad rating trend = "Skip" (they're struggling, may blame service provider)
- National franchises = "Skip"

Your response must be VALID JSON with these exact fields (no markdown, no code blocks):
{{
    "lead_type": "hot|warm|cold|skip",
    "call_priority": "Call Now|Maybe Later|Skip",
    "recommended_offer": "[offer name from list above]",
    "main_problem": "[biggest issue preventing leads/sales]",
    "why_this_lead_matters": "[2-3 sentence explanation]",
    "cold_call_opener": "[direct, blue-collar opening line - no fluff]",
    "short_pitch": "[1-2 sentence pitch for the main offer]",
    "follow_up_sms": "[casual text-style SMS follow-up - max 160 chars]",
    "follow_up_email": "[short email follow-up - 3-4 sentences]",
    "crm_note": "[internal note about the opportunity]",
    "sales_opportunity_score": [0-100 integer]
}}

Be direct and blue-collar. No corporate fluff. Think about phone calls, estimates, booked jobs.
Only include logic that focuses on conversions - calls, quotes, and customer action.
"""
        
        try:
            if self.model == "anthropic":
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": context}
                    ]
                )
                analysis_text = response.content[0].text
            else:
                response = self.client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": context}
                    ]
                )
                analysis_text = response.choices[0].message.content
            
            # Parse JSON response
            analysis = json.loads(analysis_text)
            
            # Validate required fields
            required_fields = [
                "lead_type", "call_priority", "recommended_offer",
                "main_problem", "why_this_lead_matters",
                "cold_call_opener", "short_pitch",
                "follow_up_sms", "follow_up_email", "crm_note",
                "sales_opportunity_score"
            ]
            
            for field in required_fields:
                if field not in analysis:
                    logger.warning(f"Missing field {field} in AI response")
                    analysis[field] = ""
            
            return analysis
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}")
            return self._default_analysis()
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return self._default_analysis()
    
    def _default_analysis(self) -> Dict:
        """Return default analysis when AI fails"""
        return {
            "lead_type": "cold",
            "call_priority": "Maybe Later",
            "recommended_offer": "Website Review Needed",
            "main_problem": "Unable to analyze",
            "why_this_lead_matters": "Requires manual review",
            "cold_call_opener": "Hey, quick question...",
            "short_pitch": "We help tree companies book more jobs online.",
            "follow_up_sms": "Let's chat about your online presence?",
            "follow_up_email": "Hi - I noticed your business and had an idea. Can we chat briefly?",
            "crm_note": "AI analysis failed - needs manual review",
            "sales_opportunity_score": 0
        }


def get_analyzer(model: str = AI_MODEL) -> LeadAnalyzer:
    return LeadAnalyzer(model)
