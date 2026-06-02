# Tree Lead Ranker 🌲

A repeatable lead intelligence tool for finding high-value tree service companies by state, city, and qualification metrics.

## What It Does

Tree Lead Ranker scans tree service companies in any city and scores them based on:
- **Website quality** (0-100 graded A, B, C, D, F, Broken, or No Website)
- **Sales opportunity** (0-100 based on multiple factors)
- **Lead priority** (Call Now, Maybe Later, Skip)
- **Specific offer matching** (website build, repair, redesign, or advanced marketing)

Perfect for outbound sales outreach to tree service companies who need online presence help.

## Features

### Data Collection
- ✅ Google Places API integration (not Google scraping)
- ✅ Multi-search term queries (tree service, removal, trimming, arborist, stump, land clearing)
- ✅ Business name, phone, address, city, state, rating, review count
- ✅ Website URLs and Google listing URLs

### Deduplication (Stage 2)
- ✅ Place ID matching
- ✅ Phone number normalization
- ✅ Website domain matching
- ✅ Normalized business name + city matching

### Website Auditing (Stage 3)
- ✅ HTTPS/SSL check
- ✅ Mobile viewport detection
- ✅ Phone number visibility
- ✅ Click-to-call links
- ✅ Contact forms
- ✅ Quote/estimate CTAs
- ✅ Service pages
- ✅ Location/service area pages
- ✅ Reviews/testimonials
- ✅ Before/after galleries
- ✅ Title tag, meta description
- ✅ Outdated design signals

### Scoring & Grading (Stage 4)
- ✅ Website quality score (0-100)
- ✅ Letter grades (A, B, C, D, F)
- ✅ Sales opportunity score (0-100)
- ✅ Lead type classification

### AI Analysis (Stage 5)
- ✅ Lead type (hot, warm, cold, skip)
- ✅ Call priority (Call Now, Maybe Later, Skip)
- ✅ Recommended offer matching
- ✅ Main problem identification
- ✅ Cold call openers
- ✅ Short pitches
- ✅ Follow-up SMS templates
- ✅ Follow-up email templates
- ✅ CRM notes

### Dashboard (Stage 7)
- ✅ State and city selector
- ✅ One-click scan button
- ✅ Real-time statistics
- ✅ Filterable lead table
- ✅ Expandable row details
- ✅ Copy-to-clipboard for openers, SMS, emails, CRM notes
- ✅ CSV export

## Setup

### Prerequisites
- Python 3.9+
- Google Places API key
- Anthropic API key (or OpenAI for AI analysis)

### 1. Install Dependencies

```bash
cd tree-lead-ranker
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
# Edit .env and add your API keys
```

**Get Google Places API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Places API" and "Maps JavaScript API"
4. Create API key (credentials > API key)
5. Add key to .env

**Get Anthropic API Key:**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create API key
3. Add to .env

### 3. Run the Server

```bash
python main.py
```

Server will start at `http://localhost:8000`

### 4. Open Dashboard

Open `dashboard.html` in your browser. The dashboard will connect to the local API.

Or serve it:
```bash
python -m http.server 8001
# Open http://localhost:8001/dashboard.html
```

## Usage

### Basic Workflow

1. **Select state** (South Carolina, North Carolina, Georgia)
2. **Select city** (auto-populated from state)
3. **Click "Scan City"** - this will:
   - Search Google Places for all tree service terms
   - Fetch business details
   - Audit each website
   - Score and grade websites
   - Run AI analysis on each lead
   - Save to database
4. **View results** in real-time as they're processed
5. **Filter by** Call Now, No Website, Broken Site, Grade F, 50+ reviews
6. **Click rows** to expand and see:
   - Recommended offer
   - Main problem
   - Cold call opener (copy-to-clipboard)
   - Short pitch
   - Follow-up SMS template
   - Follow-up email template
   - CRM note
7. **Export as CSV** for your CRM or spreadsheet

### Filters

- **All** - Show all leads
- **Call Now** - High-priority, actionable leads
- **No Website** - Companies without websites (offer: $500 starter site)
- **Broken Website** - Non-functional sites (offer: $700 repair/rebuild)
- **Grade F** - Very poor websites (offer: $700 redesign)
- **50+ Reviews** - Established, busy companies

### Offer Matching Rules

The AI automatically matches offers based on website status and metrics:

| Condition | Offer |
|-----------|-------|
| No website + 20+ reviews | $500 starter website + $99/mo |
| Broken website + 20+ reviews | $700 repair/rebuild + $99/mo |
| Bad website + 50+ reviews | $700 redesign + $99/mo |
| Bad website + no quote form | High priority |
| Good website | Advanced marketing/CRM suite |

### CSV Export

Export includes all fields for use in your CRM, email system, or spreadsheet:
- business_name, phone, address, city, state
- rating, review_count, website_url
- website_grade, website_quality_score
- sales_opportunity_score
- lead_type, call_priority, recommended_offer
- main_problem, cold_call_opener
- follow_up_sms, follow_up_email
- crm_note
- date_scanned

## Development Stages

### Stage 1: Scan One City ✅
- Google Places API integration
- Search 6 tree service terms
- Collect business data

### Stage 2: Save & Deduplicate ✅
- SQLite database
- Deduplication by place ID, phone, domain, name+city

### Stage 3: Audit Websites ✅
- HTTP requests and BeautifulSoup parsing
- Check 13 audit items
- Capture title tags, meta descriptions

### Stage 4: Score & Grade ✅
- Website quality scoring (0-100)
- Letter grades (A, B, C, D, F)
- Sales opportunity score (0-100)

### Stage 5: AI Analysis ✅
- Cold call openers
- Short pitches
- Follow-up SMS/email
- CRM notes

### Stage 6: CSV Export ✅
- All lead data exportable
- 19 columns

### Stage 7: Dashboard ✅
- State/city selector
- One-click scan
- Real-time stats
- Filterable table
- Copy-to-clipboard
- CSV export button

## Database Schema

### businesses table
```
- id (primary key)
- place_id (unique)
- business_name, phone, address, city, state
- category, rating, review_count
- website_url, google_listing_url
- normalized_name, domain
- website_status (no_website, broken, facebook_only, working)
- website_reachable, https, mobile_viewport, phone_visible
- click_to_call, contact_form, quote_cta
- service_pages, location_pages, reviews_testimonials
- before_after_gallery, title_tag, meta_description
- outdated_design
- website_quality_score (0-100)
- website_grade (A, B, C, D, F, Broken, No Website)
- lead_type, call_priority, recommended_offer
- main_problem, why_this_lead_matters
- cold_call_opener, short_pitch
- follow_up_sms, follow_up_email
- crm_note
- sales_opportunity_score (0-100)
- date_added, date_scanned
- is_duplicate, duplicate_of_id
```

## API Endpoints

### GET /
Health check

### GET /states
Get all states and cities

### GET /states/{state_code}/cities
Get cities for a state

### POST /scan
Start a scan (async, background task)
```json
{
  "state": "SC",
  "city": "Charleston"
}
```

### GET /leads
Get all leads (with optional filters)

### GET /leads/{lead_id}
Get single lead

### GET /export/csv?state=SC
Export leads as CSV

### GET /stats
Get scanning statistics

## Customization

### Add More States
Edit `config.py`, `STATES_AND_CITIES`:
```python
"TX": {
    "state_name": "Texas",
    "cities": ["Austin", "Dallas", "Houston", ...]
}
```

### Change AI Model
Edit `config.py`:
```python
AI_MODEL = "openai"  # or "anthropic"
```

### Adjust Website Audit Items
Edit `website_auditor.py`, `audit_website()` method

### Modify Lead Scoring
Edit `lead_analyzer.py`, `analyze_lead()` method

## Sales Pitch Style

The tool generates copy in a **direct, blue-collar style**:
- No corporate fluff
- Focused on calls, estimates, booked jobs
- No guaranteed results
- Simple language
- Action-oriented

Example opener:
> "Hey [name], I noticed you're the go-to tree guys in [city] - you've got great reviews. I help companies like you book more jobs online. Got 2 minutes?"

## Rate Limits

- Google Places API: 0.5s between requests
- API pagination: 2s between pages
- Website auditing: Timeout 10s per request
- AI analysis: 1 request per lead

## Troubleshooting

### "GOOGLE_PLACES_API_KEY not set"
- Copy `.env.example` to `.env`
- Add your actual API key to `.env`

### Scan completes but no results
- Check API key has Places API enabled
- Verify city name matches config
- Check browser console for errors

### Website audit shows all "False"
- Domain may not be extracting correctly
- Website may be down
- Timeout issue (set timeout higher in `website_auditor.py`)

### AI analysis returns empty fields
- Check ANTHROPIC_API_KEY is set and valid
- Check rate limits (may need to space requests out)
- Review error logs in terminal

## Next Steps

1. **Scale to more states** - Add 10+ states in `config.py`
2. **Custom scoring rules** - Adjust lead_analyzer.py for your service areas
3. **CRM integration** - Add Zapier/webhook to push leads to your CRM
4. **Outbound automation** - Use call list with SMS/email sequences
5. **Performance tracking** - Log which offers convert best

## License

Built for you. Use it freely, modify as needed.

## Support

Check the code comments and docstrings for details. Each module is self-contained:
- `places_api.py` - Google Places integration
- `website_auditor.py` - Website analysis
- `lead_analyzer.py` - AI scoring
- `deduplicator.py` - Duplicate detection
- `models.py` - Database schema
- `main.py` - FastAPI routes

Good luck with your outreach! 🚀
