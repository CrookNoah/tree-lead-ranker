"""
Outreach Automation

Auto-send SMS and emails to leads based on priority and timing.
Turns scanning into automatic follow-up sequences.

Features:
- Send SMS immediately to Call Now leads
- Schedule emails (Day 1, Day 3, Day 7)
- Track sent messages (know what you sent)
- Smart timing (don't spam during off-hours)
- Customizable templates
"""

from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)

class OutreachType(Enum):
    SMS = "sms"
    EMAIL = "email"

class OutreachStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    SENT = "sent"
    FAILED = "failed"
    OPTED_OUT = "opted_out"

class OutreachManager:
    """Manage automated outreach campaigns"""
    
    def __init__(self, twilio_account_sid=None, twilio_auth_token=None, twilio_phone=None):
        """
        Initialize outreach manager with optional Twilio credentials.
        If credentials not provided, SMS features will be disabled (dry run mode).
        """
        self.twilio_enabled = False
        self.twilio_phone = twilio_phone
        
        if twilio_account_sid and twilio_auth_token:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(twilio_account_sid, twilio_auth_token)
                self.twilio_enabled = True
                logger.info("Twilio SMS enabled")
            except ImportError:
                logger.warning("Twilio not installed. SMS features disabled. Run: pip install twilio")
            except Exception as e:
                logger.warning(f"Twilio setup failed: {e}. SMS features disabled.")
        else:
            logger.info("Twilio credentials not provided. SMS features in dry-run mode.")
    
    # ====== SMS OUTREACH ======
    
    def should_send_sms(self, lead: Dict) -> bool:
        """Determine if lead qualifies for SMS outreach"""
        # Only auto-send to Call Now leads
        if lead.get("call_priority") != "Call Now":
            return False
        
        # Don't send if they've opted out
        if lead.get("opted_out_sms"):
            return False
        
        # Don't send if already sent
        if lead.get("sms_sent"):
            return False
        
        # Only if we have their phone
        if not lead.get("phone"):
            return False
        
        return True
    
    def send_sms(self, lead: Dict, message: str = None) -> Dict:
        """
        Send SMS to lead.
        
        If message not provided, uses lead.follow_up_sms
        """
        if not self.should_send_sms(lead):
            return {
                "success": False,
                "reason": "Lead doesn't qualify for SMS",
                "message": None,
            }
        
        phone = lead.get("phone")
        message = message or lead.get("follow_up_sms", "")
        
        if not message:
            return {
                "success": False,
                "reason": "No message to send",
                "message": None,
            }
        
        # Ensure message fits SMS length (160 chars)
        if len(message) > 160:
            message = message[:157] + "..."
        
        result = self._send_sms_via_twilio(phone, message)
        
        logger.info(
            f"SMS to {lead['business_name']} ({phone}): "
            f"{'✓ sent' if result['success'] else '✗ failed'}"
        )
        
        return result
    
    def _send_sms_via_twilio(self, phone: str, message: str) -> Dict:
        """Actually send SMS via Twilio API"""
        if not self.twilio_enabled:
            logger.info(f"DRY RUN: SMS to {phone}: {message}")
            return {
                "success": True,
                "type": "sms",
                "phone": phone,
                "message": message,
                "sent_at": datetime.now().isoformat(),
                "dry_run": True,
            }
        
        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone,
                to=phone,
            )
            
            return {
                "success": True,
                "type": "sms",
                "phone": phone,
                "message": message,
                "sid": message_obj.sid,
                "sent_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"SMS send failed for {phone}: {e}")
            return {
                "success": False,
                "type": "sms",
                "phone": phone,
                "message": message,
                "error": str(e),
            }
    
    # ====== EMAIL OUTREACH ======
    
    def get_email_sequences(self) -> Dict[str, List[Dict]]:
        """
        Define email sequences by lead priority.
        
        Returns dict mapping priority → sequence of emails
        Each email: {delay_days, subject, body}
        """
        return {
            "Call Now": [
                {
                    "delay_days": 0,
                    "subject": "Quick idea for {business_name}",
                    "body": """Hi {first_name},

Just had a quick thought about {business_name}. 

I noticed your Google reviews are solid, but your website might be leaving money on the table. 

Would it be worth a quick 10-minute call to see if I'm right?

{signature}
"""
                },
                {
                    "delay_days": 3,
                    "subject": "Re: Your online presence",
                    "body": """Hey {first_name},

Following up on my earlier message. I work with tree companies in {city} to help them book more jobs online.

No pressure — just thought it was worth reaching out.

If you're open to it, I can show you exactly what's working for your competitors.

{signature}
"""
                },
                {
                    "delay_days": 7,
                    "subject": "{business_name} — last message",
                    "body": """Hi {first_name},

I'll keep this short. Most tree companies are losing 30-40% of potential leads due to poor online presence.

I help fix that.

If you'd like to see how, let me know.

{signature}
"""
                },
            ],
            "Maybe Later": [
                {
                    "delay_days": 1,
                    "subject": "Hi {first_name} from {city}",
                    "body": """Hi {first_name},

I help tree companies improve their online presence and book more jobs.

Saw {business_name} and thought you might find it useful.

No obligation — just reaching out.

{signature}
"""
                },
                {
                    "delay_days": 7,
                    "subject": "When you're ready to grow",
                    "body": """Hey {first_name},

When {business_name} is ready to invest in growth, I've got some proven ideas.

No rush — just wanted to be on your radar.

{signature}
"""
                },
            ],
        }
    
    def should_send_email(self, lead: Dict, sequence_step: int = 0) -> bool:
        """Determine if lead qualifies for email at this step"""
        # Skip if opted out
        if lead.get("opted_out_email"):
            return False
        
        # Skip if on "Skip" priority
        if lead.get("call_priority") == "Skip":
            return False
        
        # Don't send if no email
        if not lead.get("email"):
            return False
        
        # Check if already sent this sequence step
        sent_emails = lead.get("emails_sent", [])
        if len(sent_emails) > sequence_step:
            return False
        
        return True
    
    def schedule_email(self, lead: Dict, sequence_key: str = None) -> Dict:
        """
        Schedule email sequence for lead.
        
        Determines sequence type from lead priority automatically.
        """
        if not sequence_key:
            sequence_key = lead.get("call_priority", "Maybe Later")
        
        sequences = self.get_email_sequences()
        if sequence_key not in sequences:
            return {
                "success": False,
                "reason": f"Unknown sequence: {sequence_key}",
            }
        
        sequence = sequences[sequence_key]
        scheduled = []
        
        for i, email_template in enumerate(sequence):
            send_at = datetime.now() + timedelta(days=email_template["delay_days"])
            
            scheduled.append({
                "step": i,
                "subject": email_template["subject"],
                "body": email_template["body"],
                "send_at": send_at.isoformat(),
                "status": "scheduled",
            })
        
        logger.info(
            f"Scheduled {len(scheduled)} emails for {lead['business_name']} "
            f"({sequence_key})"
        )
        
        return {
            "success": True,
            "lead_id": lead.get("id"),
            "sequence": sequence_key,
            "emails": scheduled,
        }
    
    def get_pending_emails(self, db) -> List[Dict]:
        """
        Get all emails that are due to send now.
        (In production, would query database for scheduled emails)
        """
        # This would query the outreach_messages table
        # For now, returns empty (would be integrated with database)
        return []
    
    # ====== TEMPLATES & PERSONALIZATION ======
    
    def personalize_message(self, template: str, lead: Dict) -> str:
        """Replace template variables with lead data"""
        replacements = {
            "{business_name}": lead.get("business_name", "friend"),
            "{first_name}": self._extract_first_name(lead.get("business_name", "there")),
            "{city}": lead.get("city", "your area"),
            "{state}": lead.get("state", "your area"),
            "{phone}": lead.get("phone", "[phone]"),
            "{website}": lead.get("website_url", ""),
            "{rating}": f"{lead.get('rating', 0):.1f}",
            "{reviews}": str(lead.get("review_count", 0)),
            "{signature}": self._get_signature(),
        }
        
        result = template
        for placeholder, value in replacements.items():
            result = result.replace(placeholder, value)
        
        return result
    
    def _extract_first_name(self, business_name: str) -> str:
        """Try to extract first name from business name"""
        # "John's Tree Service" → "John"
        # "Smith Tree Company" → "Smith"
        # Default: just use first word
        parts = business_name.split()
        if parts:
            name = parts[0].replace("'s", "").replace("'", "")
            return name
        return "there"
    
    def _get_signature(self) -> str:
        """Get email signature"""
        return """Best,
[Your Name]
[Your Company]
[Your Phone]
[Your Email]"""
    
    # ====== CAMPAIGN MANAGEMENT ======
    
    def create_campaign(
        self,
        name: str,
        leads: List[Dict],
        sms_enabled: bool = True,
        email_enabled: bool = True,
    ) -> Dict:
        """
        Create outreach campaign for a list of leads.
        
        Returns campaign summary with stats.
        """
        campaign = {
            "name": name,
            "created_at": datetime.now().isoformat(),
            "total_leads": len(leads),
            "sms_sent": 0,
            "sms_failed": 0,
            "emails_scheduled": 0,
            "details": [],
        }
        
        for lead in leads:
            lead_result = {
                "lead_id": lead.get("id"),
                "business_name": lead.get("business_name"),
                "sms": None,
                "email": None,
            }
            
            # Send SMS
            if sms_enabled and self.should_send_sms(lead):
                sms_result = self.send_sms(lead)
                lead_result["sms"] = sms_result
                if sms_result["success"]:
                    campaign["sms_sent"] += 1
                else:
                    campaign["sms_failed"] += 1
            
            # Schedule Email
            if email_enabled and self.should_send_email(lead):
                email_result = self.schedule_email(lead)
                lead_result["email"] = email_result
                if email_result["success"]:
                    campaign["emails_scheduled"] += len(email_result.get("emails", []))
            
            campaign["details"].append(lead_result)
        
        logger.info(
            f"Campaign '{name}': {campaign['sms_sent']} SMS sent, "
            f"{campaign['emails_scheduled']} emails scheduled"
        )
        
        return campaign
    
    def get_campaign_stats(self, campaign: Dict) -> str:
        """Return human-readable campaign summary"""
        stats = f"""
Campaign: {campaign['name']}
Created: {campaign['created_at']}

Results:
  Total leads: {campaign['total_leads']}
  SMS sent: {campaign['sms_sent']}
  SMS failed: {campaign['sms_failed']}
  Emails scheduled: {campaign['emails_scheduled']}

Details by lead:
"""
        for detail in campaign["details"]:
            stats += f"\n  • {detail['business_name']}"
            if detail["sms"]:
                stats += f" [SMS: {'✓' if detail['sms']['success'] else '✗'}]"
            if detail["email"]:
                stats += f" [Emails: ✓ {len(detail['email'].get('emails', []))}]"
        
        return stats


def get_outreach_manager(
    twilio_account_sid: Optional[str] = None,
    twilio_auth_token: Optional[str] = None,
    twilio_phone: Optional[str] = None,
) -> OutreachManager:
    """Factory function to create outreach manager"""
    return OutreachManager(twilio_account_sid, twilio_auth_token, twilio_phone)
