"""
ROI Calculator

Show tree service businesses the money impact of improving their online presence.

The pitch "you need a website" doesn't work.
The pitch "a website will get you 8-12 extra jobs per month = $50k/year" works.

This module calculates:
- Current estimated revenue (from review count)
- Lost leads from poor online presence
- Revenue upside from improvement
- ROI of each offer (payback period)
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ROICalculator:
    """Calculate ROI of digital marketing offers"""
    
    # Tree service industry benchmarks
    BENCHMARKS = {
        # Average job value by service type
        "tree_removal": 1200,
        "tree_trimming": 450,
        "stump_grinding": 350,
        "land_clearing": 2500,
        "general": 800,
        
        # Seasonal revenue distribution
        "seasonal": {
            1: 0.6,   # January - slow (60% of average)
            2: 0.8,
            3: 1.2,
            4: 1.4,
            5: 1.3,
            6: 0.8,
            7: 0.5,   # July - summer slow
            8: 0.6,
            9: 1.1,
            10: 1.4,
            11: 1.3,
            12: 0.8,
        },
        
        # Conversion metrics
        "calls_to_jobs": 0.15,      # 15% of calls = booked jobs
        "website_improvement_lift": 0.25,  # 25% more leads from good website
        "lost_lead_percentage": {
            "no_website": 0.40,         # Lose 40% of potential leads
            "broken_website": 0.25,     # Lose 25% of potential leads
            "bad_website": 0.15,        # Lose 15% of potential leads
            "okay_website": 0.05,       # Lose 5% of potential leads
        },
    }
    
    def calculate_roi(self, business: Dict) -> Dict:
        """Calculate comprehensive ROI for a business"""
        
        roi = {
            "business_name": business.get("business_name"),
            "current_state": self._analyze_current_state(business),
            "improvement_scenarios": self._calculate_improvement_scenarios(business),
            "recommended_offer": self._recommend_offer(business),
            "pitch": self._generate_pitch(business),
        }
        
        return roi
    
    def _analyze_current_state(self, business: Dict) -> Dict:
        """Analyze current business state"""
        
        # Estimate current monthly revenue
        monthly_jobs = self._estimate_monthly_jobs(business)
        job_value = self._estimate_job_value(business)
        current_monthly_revenue = monthly_jobs * job_value
        current_annual_revenue = current_monthly_revenue * 12
        
        # Estimate lost leads
        website_status = business.get("website_status", "no_website")
        lost_percentage = self.BENCHMARKS["lost_lead_percentage"].get(website_status, 0.2)
        estimated_lost_jobs = monthly_jobs * (lost_percentage / (1 - lost_percentage))
        estimated_lost_revenue = estimated_lost_jobs * job_value
        
        return {
            "monthly_jobs": int(monthly_jobs),
            "job_value": int(job_value),
            "monthly_revenue": int(current_monthly_revenue),
            "annual_revenue": int(current_annual_revenue),
            "website_status": website_status,
            "estimated_lost_jobs_monthly": int(estimated_lost_jobs),
            "estimated_lost_revenue_monthly": int(estimated_lost_revenue),
            "estimated_lost_revenue_yearly": int(estimated_lost_revenue * 12),
        }
    
    def _estimate_monthly_jobs(self, business: Dict) -> float:
        """Estimate monthly jobs from review count"""
        
        review_count = business.get("review_count", 0)
        
        # Rough heuristic: established tree company gets 0.5-2 new reviews/job
        # So review_count / 1.5 = rough lifetime jobs
        # Then estimate jobs per month
        
        if review_count >= 200:
            # Very busy: ~3-4 jobs/month
            return 3.5
        elif review_count >= 100:
            # Busy: ~2-3 jobs/month
            return 2.5
        elif review_count >= 50:
            # Moderate: ~1.5-2 jobs/month
            return 1.75
        elif review_count >= 20:
            # Slower: ~0.8-1.2 jobs/month
            return 1.0
        elif review_count >= 10:
            return 0.5
        else:
            return 0.2
    
    def _estimate_job_value(self, business: Dict) -> float:
        """Estimate average job value"""
        
        category = business.get("category", [])
        
        # Check service type from category
        if isinstance(category, str):
            category = [category]
        
        category_str = " ".join(category).lower()
        
        if "stump" in category_str:
            return self.BENCHMARKS["stump_grinding"]
        elif "clearing" in category_str or "land" in category_str:
            return self.BENCHMARKS["land_clearing"]
        elif "trimming" in category_str or "pruning" in category_str:
            return self.BENCHMARKS["tree_trimming"]
        elif "removal" in category_str:
            return self.BENCHMARKS["tree_removal"]
        else:
            return self.BENCHMARKS["general"]
    
    def _calculate_improvement_scenarios(self, business: Dict) -> Dict:
        """Calculate ROI of different improvement scenarios"""
        
        current_state = self._analyze_current_state(business)
        job_value = current_state["job_value"]
        current_monthly_jobs = current_state["monthly_jobs"]
        
        scenarios = {}
        
        # Scenario 1: Website improvement (all levels → good website)
        website_improvement = {
            "name": "Website Improvement",
            "improvement": self.BENCHMARKS["website_improvement_lift"],
            "monthly_job_increase": current_monthly_jobs * self.BENCHMARKS["website_improvement_lift"],
            "monthly_revenue_increase": (
                current_monthly_jobs * self.BENCHMARKS["website_improvement_lift"] * job_value
            ),
            "annual_revenue_increase": (
                current_monthly_jobs * self.BENCHMARKS["website_improvement_lift"] * job_value * 12
            ),
        }
        scenarios["website_improvement"] = website_improvement
        
        # Scenario 2: Recover lost leads
        website_status = business.get("website_status", "no_website")
        lost_percentage = self.BENCHMARKS["lost_lead_percentage"].get(website_status, 0.2)
        
        # If we fix the website, we get these lost leads back
        recovered_jobs = current_monthly_jobs * (lost_percentage / (1 - lost_percentage))
        
        lost_lead_recovery = {
            "name": "Recover Lost Leads",
            "improvement": lost_percentage,
            "monthly_job_increase": recovered_jobs,
            "monthly_revenue_increase": recovered_jobs * job_value,
            "annual_revenue_increase": recovered_jobs * job_value * 12,
        }
        scenarios["recover_lost_leads"] = lost_lead_recovery
        
        # Scenario 3: Combined (website improvement + lost lead recovery)
        combined_jobs = (
            current_monthly_jobs * self.BENCHMARKS["website_improvement_lift"] + 
            recovered_jobs
        )
        
        combined = {
            "name": "Combined Impact",
            "monthly_job_increase": combined_jobs,
            "monthly_revenue_increase": combined_jobs * job_value,
            "annual_revenue_increase": combined_jobs * job_value * 12,
        }
        scenarios["combined"] = combined
        
        return scenarios
    
    def _recommend_offer(self, business: Dict) -> Dict:
        """Recommend which offer has best ROI"""
        
        website_status = business.get("website_status", "no_website")
        website_grade = business.get("website_grade", "F")
        roi = self._analyze_current_state(business)
        improvements = self._calculate_improvement_scenarios(business)
        
        recommendations = {
            "offer": None,
            "price": None,
            "monthly_revenue_impact": None,
            "annual_revenue_impact": None,
            "payback_period_months": None,
            "roi_percentage": None,
            "reasoning": None,
        }
        
        # No website
        if website_status == "no_website":
            recommendations.update({
                "offer": "Starter Website + Hosting",
                "price": 500 + (99 * 12),  # First year = $500 + 12mo hosting
                "monthly_revenue_impact": improvements["recover_lost_leads"]["monthly_revenue_increase"],
                "annual_revenue_impact": improvements["recover_lost_leads"]["annual_revenue_increase"],
            })
            reasoning = (
                f"You're getting {roi['monthly_jobs']} new jobs/month despite NO WEBSITE. "
                f"That means you're losing ~${roi['estimated_lost_revenue_monthly']}/month ({int(roi['estimated_lost_revenue_monthly']/roi['monthly_revenue']*100)}% of potential revenue) to poor online presence. "
                f"A website would recover this, getting you {int(improvements['recover_lost_leads']['monthly_job_increase'])} extra jobs/month = ${int(improvements['recover_lost_leads']['monthly_revenue_increase'])}/month."
            )
        
        # Broken website
        elif website_status == "broken":
            recommendations.update({
                "offer": "Website Repair/Rebuild + Hosting",
                "price": 700 + (99 * 12),
                "monthly_revenue_impact": improvements["recover_lost_leads"]["monthly_revenue_increase"],
                "annual_revenue_impact": improvements["recover_lost_leads"]["annual_revenue_impact"],
            })
            reasoning = (
                f"Your website is broken, so you're losing ~${roi['estimated_lost_revenue_monthly']}/month in potential leads. "
                f"Fixing it would give you {int(improvements['recover_lost_leads']['monthly_job_increase'])} extra jobs/month = ${int(improvements['recover_lost_leads']['monthly_revenue_increase'])}/month."
            )
        
        # Bad website
        elif website_grade in ["F", "D", "C"]:
            recommendations.update({
                "offer": "Website Redesign + Hosting",
                "price": 700 + (99 * 12),
                "monthly_revenue_impact": improvements["combined"]["monthly_revenue_increase"],
                "annual_revenue_impact": improvements["combined"]["annual_revenue_increase"],
            })
            reasoning = (
                f"Your website is losing you ~${roi['estimated_lost_revenue_monthly']}/month, plus another ${int(roi['monthly_revenue'] * 0.25)}/month "
                f"from poor conversion. A redesign + improvement would get you {int(improvements['combined']['monthly_job_increase'])} extra jobs/month = "
                f"${int(improvements['combined']['monthly_revenue_increase'])}/month."
            )
        
        # Decent/good website
        else:
            recommendations.update({
                "offer": "SEO + Marketing Optimization",
                "price": 1500,  # Monthly recurring
                "monthly_revenue_impact": int(improvements["website_improvement"]["monthly_revenue_increase"]),
                "annual_revenue_impact": int(improvements["website_improvement"]["annual_revenue_increase"]),
            })
            reasoning = (
                f"Your website is solid. The opportunity is in driving more qualified traffic to it. "
                f"With proper SEO and optimization, you could get {int(improvements['website_improvement']['monthly_job_increase'])} extra jobs/month = "
                f"${int(improvements['website_improvement']['monthly_revenue_increase'])}/month."
            )
        
        # Calculate payback period
        monthly_impact = recommendations.get("monthly_revenue_impact", 0)
        if recommendations.get("price") and monthly_impact > 0:
            payback_months = recommendations["price"] / monthly_impact
            recommendations["payback_period_months"] = round(payback_months, 1)
            recommendations["roi_percentage"] = round(
                (recommendations.get("annual_revenue_impact", 0) / recommendations.get("price", 1)) * 100,
                0
            )
        
        recommendations["reasoning"] = reasoning
        
        return recommendations
    
    def _generate_pitch(self, business: Dict) -> str:
        """Generate data-driven sales pitch"""
        
        current = self._analyze_current_state(business)
        recommendation = self._recommend_offer(business)
        
        pitch = f"""
Based on your {current['monthly_jobs']} monthly jobs and {current['job_value']} average job value:

Current Situation:
• Monthly revenue: ~${current['monthly_revenue']:,}
• Annual revenue: ~${current['annual_revenue']:,}
• Lost to poor online presence: ${current['estimated_lost_revenue_monthly']:,}/month (${current['estimated_lost_revenue_yearly']:,}/year)

With {recommendation['offer']}:
• Additional revenue: ${recommendation['monthly_revenue_impact']:,}/month
• Annual upside: ${recommendation['annual_revenue_impact']:,}/year
• Investment payback: {recommendation['payback_period_months']} months
• Year 1 ROI: {int(recommendation['roi_percentage'])}%

Why this matters:
{recommendation['reasoning']}
"""
        return pitch.strip()
    
    def get_pitch(self, business: Dict) -> str:
        """Get formatted pitch for cold calling"""
        roi_data = self.calculate_roi(business)
        return roi_data["pitch"]
    
    def get_cta(self, business: Dict) -> str:
        """Get call-to-action based on ROI"""
        recommendation = self._recommend_offer(business)
        
        if recommendation["payback_period_months"] < 1:
            return f"This pays for itself in {int(recommendation['payback_period_months'] * 30)} days. When can we start?"
        elif recommendation["payback_period_months"] < 3:
            return f"Your investment pays for itself in {int(recommendation['payback_period_months'])} months. Can we talk this week?"
        elif recommendation["payback_period_months"] < 6:
            return f"With ${recommendation['annual_revenue_impact']:,} annual upside, this is worth exploring. When's good for a quick call?"
        else:
            return f"This could add ${recommendation['annual_revenue_impact']:,} to your annual revenue. Worth 15 minutes?"


def get_roi_calculator() -> ROICalculator:
    return ROICalculator()
