"""
Behavioral Lead Scoring

Score leads by activity signals (more predictive of buying intent than website quality alone):
- Recent review activity (last 30 days = actively getting customers)
- Review sentiment trend (improving = business growing)
- Website freshness (recent updates = spending money)
- Social media activity (posting frequency = marketing awareness)
- Seasonal patterns (busy months = cash on hand)
- Google My Business engagement (photos, responses = active management)

A mediocre website with hot activity = hotter lead than perfect website with no activity.
"""

from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)

class BehavioralScorer:
    def __init__(self):
        self.timeout = 10
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    def score_behavior(self, business: Dict) -> Dict:
        """
        Score behavioral signals for a business.
        
        Returns dict with:
        - activity_score (0-100): How active/engaged is the business?
        - activity_breakdown: Individual scores for each signal
        - signals: Specific findings
        - readiness_assessment: Hot/Warm/Cold based on activity
        """
        
        scores = {
            "recent_reviews": 0,
            "sentiment_trend": 0,
            "website_freshness": 0,
            "social_activity": 0,
            "gmb_engagement": 0,
            "seasonal_strength": 0,
        }
        
        signals = {
            "recent_review_count": 0,
            "review_trend": "unknown",  # improving, stable, declining
            "last_review_date": None,
            "website_last_update": None,
            "social_platforms": [],
            "posting_frequency": None,  # posts/month
            "gmb_response_rate": None,
            "is_peak_season": False,
            "busy_months": [],
        }
        
        # Score 1: Recent Review Activity
        if business.get("review_count", 0) > 0:
            # Google doesn't give us review dates, but we can estimate:
            # If they have lots of reviews and high count, they're probably getting recent ones
            avg_reviews_per_month = business.get("review_count", 0) / max(1, 12)  # Rough estimate
            
            # Hot signal: 3+ reviews per month = actively getting customers
            if avg_reviews_per_month >= 3:
                scores["recent_reviews"] = 95
                signals["recent_review_count"] = business["review_count"]
            elif avg_reviews_per_month >= 1.5:
                scores["recent_reviews"] = 70
                signals["recent_review_count"] = business["review_count"]
            elif avg_reviews_per_month >= 0.5:
                scores["recent_reviews"] = 40
            else:
                scores["recent_reviews"] = 10
        
        # Score 2: Review Sentiment Trend
        sentiment_score = self._analyze_review_sentiment(business)
        scores["sentiment_trend"] = sentiment_score["score"]
        signals["review_trend"] = sentiment_score["trend"]
        
        # Score 3: Website Freshness
        if business.get("website_url"):
            freshness = self._check_website_freshness(business["website_url"])
            scores["website_freshness"] = freshness["score"]
            signals["website_last_update"] = freshness["last_update"]
        
        # Score 4: Social Media Activity
        if business.get("business_name") and business.get("city"):
            social = self._check_social_activity(
                business["business_name"],
                business.get("city"),
                business.get("state")
            )
            scores["social_activity"] = social["score"]
            signals["social_platforms"] = social["platforms"]
            signals["posting_frequency"] = social["posts_per_month"]
        
        # Score 5: Google My Business Engagement (estimate from website signals)
        if business.get("website_url"):
            gmb = self._estimate_gmb_engagement(business)
            scores["gmb_engagement"] = gmb["score"]
            signals["gmb_response_rate"] = gmb["response_rate"]
        
        # Score 6: Seasonal Strength
        seasonal = self._calculate_seasonal_strength(
            business.get("city"),
            business.get("state"),
            business.get("category", [])
        )
        scores["seasonal_strength"] = seasonal["score"]
        signals["is_peak_season"] = seasonal["is_peak"]
        signals["busy_months"] = seasonal["busy_months"]
        
        # Calculate overall activity score (weighted)
        weights = {
            "recent_reviews": 0.25,      # Most predictive
            "sentiment_trend": 0.15,
            "website_freshness": 0.20,   # Spending money signal
            "social_activity": 0.15,
            "gmb_engagement": 0.15,
            "seasonal_strength": 0.10,
        }
        
        activity_score = sum(
            scores[key] * weights[key]
            for key in scores.keys()
        )
        
        # Determine readiness
        if activity_score >= 75:
            readiness = "HOT - Actively growing, spending money, getting reviews"
        elif activity_score >= 55:
            readiness = "WARM - Some activity signals, mixed engagement"
        elif activity_score >= 35:
            readiness = "COLD - Minimal activity, may not be ready"
        else:
            readiness = "FROZEN - No activity signals, very low intent"
        
        return {
            "activity_score": round(activity_score, 0),
            "readiness": readiness,
            "breakdown": scores,
            "signals": signals,
            "recommendation": self._readiness_recommendation(activity_score, business),
        }
    
    def _analyze_review_sentiment(self, business: Dict) -> Dict:
        """
        Estimate review sentiment trend from available signals.
        
        In production, you'd use Google Reviews API or scraping,
        but we work with what we have.
        """
        score = 50  # Default neutral
        trend = "unknown"
        
        # High rating = likely positive trend
        rating = business.get("rating", 3.5)
        if rating >= 4.7:
            score = 90  # Consistently excellent
            trend = "improving"
        elif rating >= 4.3:
            score = 75
            trend = "stable"
        elif rating >= 3.7:
            score = 50
            trend = "stable"
        elif rating >= 3.2:
            score = 30
            trend = "declining"
        else:
            score = 10
            trend = "declining"
        
        return {"score": score, "trend": trend}
    
    def _check_website_freshness(self, url: str) -> Dict:
        """Check if website is being actively maintained."""
        score = 30
        last_update = None
        
        if not url or url.startswith("http") == False:
            url = f"https://{url}"
        
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            if response.status_code != 200:
                return {"score": 20, "last_update": None}
            
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            
            # Check for common "last updated" patterns
            body_text = soup.get_text().lower()
            
            # Look for dates in common formats
            date_patterns = [
                r"updated\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"last\s+updated\s+(\w+\s+\d{1,2},?\s+\d{4})",
                r"copyright.*(\d{4})",
                r"©\s*(\d{4})",
            ]
            
            for pattern in date_patterns:
                matches = re.findall(pattern, body_text)
                if matches:
                    last_update = matches[0]
                    break
            
            # Check for freshness signals in HTTP headers
            if "Last-Modified" in response.headers:
                last_mod = response.headers["Last-Modified"]
                # Parse date and check if recent
                try:
                    from email.utils import parsedate_to_datetime
                    mod_date = parsedate_to_datetime(last_mod)
                    days_old = (datetime.now(mod_date.tzinfo) - mod_date).days
                    
                    if days_old <= 7:
                        score = 95  # Updated this week
                    elif days_old <= 30:
                        score = 80  # Updated this month
                    elif days_old <= 90:
                        score = 60  # Updated this quarter
                    elif days_old <= 365:
                        score = 35  # Updated this year
                    else:
                        score = 10  # Hasn't been updated in over a year
                    
                    last_update = f"{days_old} days ago"
                except:
                    pass
            
            # Check for copyright year (weak signal but something)
            copyright_pattern = r"copyright.*?(\d{4})"
            copyright_matches = re.findall(copyright_pattern, body_text)
            if copyright_matches:
                year = int(copyright_matches[-1])  # Last copyright year
                current_year = datetime.now().year
                if current_year - year <= 1:
                    score = max(score, 70)
                elif current_year - year <= 2:
                    score = max(score, 50)
            
            # Check for blog/news updates (strong freshness signal)
            if soup.find("article") or soup.find(class_="post") or soup.find(class_="blog"):
                # Has blog section
                articles = soup.find_all(class_="post-date") or soup.find_all(class_="article-date")
                if articles:
                    score = max(score, 85)  # Blog is active
            
            return {"score": max(10, min(100, score)), "last_update": last_update}
        
        except Exception as e:
            logger.warning(f"Website freshness check failed for {url}: {e}")
            return {"score": 30, "last_update": None}
    
    def _check_social_activity(self, business_name: str, city: str, state: str) -> Dict:
        """
        Estimate social media activity.
        
        In production, you'd use Facebook/Instagram Graph API or LinkedIn scraping.
        For now, we estimate based on presence signals.
        """
        score = 0
        platforms = []
        posts_per_month = 0
        
        search_query = f"{business_name} {city} {state}".replace(" ", "+")
        
        # Check for Facebook presence (rough estimation)
        facebook_signal = self._check_platform_presence(
            f"site:facebook.com {search_query}",
            "facebook"
        )
        if facebook_signal["found"]:
            platforms.append("Facebook")
            score += 30
            posts_per_month += facebook_signal.get("estimated_posts", 2)
        
        # Check for Instagram presence
        instagram_signal = self._check_platform_presence(
            f"site:instagram.com {search_query}",
            "instagram"
        )
        if instagram_signal["found"]:
            platforms.append("Instagram")
            score += 35  # Instagram is more active generally
            posts_per_month += instagram_signal.get("estimated_posts", 4)
        
        # Check for Google My Business (via business name search)
        gmb_signal = self._check_platform_presence(
            f"{business_name} {city}",
            "google_my_business"
        )
        if gmb_signal["found"]:
            platforms.append("Google My Business")
            score += 25
        
        # Scoring: more platforms + more frequent posts = higher activity
        if len(platforms) >= 3:
            score = min(100, score + 20)
        elif len(platforms) == 0:
            score = 15  # No social presence
        
        # Estimate activity level
        if posts_per_month >= 8:
            score = min(100, score + 15)  # Very active
        elif posts_per_month >= 4:
            score = min(100, score + 10)  # Active
        elif posts_per_month < 1:
            score = max(10, score - 15)  # Inactive
        
        return {
            "score": max(10, min(100, score)),
            "platforms": platforms,
            "posts_per_month": posts_per_month or 2,  # Conservative estimate
        }
    
    def _check_platform_presence(self, search_query: str, platform: str) -> Dict:
        """Check if business has presence on a platform (simplified)."""
        # In production, use actual APIs
        # For MVP, assume if they have a website and reviews, likely on major platforms
        return {
            "found": False,  # Would require API key
            "estimated_posts": 2,
        }
    
    def _estimate_gmb_engagement(self, business: Dict) -> Dict:
        """
        Estimate Google My Business engagement from signals.
        
        High engagement = frequently updated GMB, responds to reviews, adds photos.
        """
        score = 40  # Default neutral
        response_rate = None
        
        # If website is well-designed and has reviews, likely managing GMB
        website_grade = business.get("website_grade", "F")
        rating = business.get("rating", 3.5)
        
        if website_grade in ["A", "B"] and rating >= 4.5:
            score = 85  # Professional operation, likely managing GMB
        elif website_grade in ["C"] or rating >= 4.0:
            score = 60
        elif website_grade in ["D", "F"] or rating <= 3.5:
            score = 35
        
        # High review count suggests they're active on GMB
        if business.get("review_count", 0) >= 100:
            score = min(100, score + 20)
        
        return {"score": score, "response_rate": response_rate}
    
    def _calculate_seasonal_strength(self, city: str, state: str, category: List) -> Dict:
        """
        Estimate business's seasonal cash position.
        
        Tree service is busiest: Spring (Mar-May) and Fall (Sept-Nov).
        Summer and winter slower, but varies by region.
        """
        score = 50  # Neutral
        is_peak = False
        busy_months = []
        
        current_month = datetime.now().month
        
        # Tree service seasonal patterns (by region)
        if state in ["SC", "NC", "GA", "FL"]:
            # South/warm climate: Earlier spring (Feb-April), late fall (Oct-Nov)
            peak_months = [2, 3, 4, 10, 11]  # Feb-Apr, Oct-Nov
            slow_months = [7, 8]  # Hot summer
            busy_months = peak_months
        elif state in ["NY", "VT", "NH", "MA"]:
            # Northern: Later spring (Apr-May), fall (Sept-Oct)
            peak_months = [4, 5, 9, 10]
            slow_months = [12, 1, 2, 3]  # Snow/frozen
            busy_months = peak_months
        else:
            # Default moderate climate
            peak_months = [3, 4, 5, 9, 10, 11]
            slow_months = [7, 8]
            busy_months = peak_months
        
        is_peak = current_month in peak_months
        
        if is_peak:
            score = 90  # Peak season = cash flowing
        elif current_month in slow_months:
            score = 20  # Slow season = less cash
        else:
            score = 55  # Shoulder season = moderate
        
        return {
            "score": score,
            "is_peak": is_peak,
            "busy_months": busy_months,
            "current_season": "PEAK" if is_peak else ("SLOW" if current_month in slow_months else "SHOULDER"),
        }
    
    def _readiness_recommendation(self, activity_score: float, business: Dict) -> str:
        """Give specific recommendation based on activity score."""
        
        if activity_score >= 80:
            return (
                "🔴 CALL IMMEDIATELY - This business is actively growing with strong activity signals. "
                "They have cash on hand (peak season/high activity), are spending money on their online presence, "
                "and are getting consistent new customers. High close rate expected."
            )
        elif activity_score >= 65:
            return (
                "🟠 CALL THIS WEEK - Good activity signals. Business is somewhat active, "
                "getting steady reviews, and likely has some marketing budget. "
                "Good conversion potential."
            )
        elif activity_score >= 50:
            return (
                "🟡 CALL NEXT WEEK - Mixed signals. Business exists and gets some traction but "
                "isn't highly active. May not be ready to invest yet. "
                "Could be good fit if in peak season or if pain point is clear."
            )
        elif activity_score >= 35:
            return (
                "⚪ LOW PRIORITY - Weak activity signals. Business seems dormant or very small. "
                "May be open to learning but low conversion likelihood. "
                "Skip unless you have specific reason to target them."
            )
        else:
            return (
                "❌ SKIP - No activity signals detected. Business may be inactive, closed, "
                "or not serious about growth. Focus on hotter leads."
            )


def get_behavioral_scorer() -> BehavioralScorer:
    return BehavioralScorer()
