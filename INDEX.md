# Tree Lead Ranker - Complete Index

## 📚 Documentation (Read in Order)

1. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
   - Get API keys
   - Configure .env
   - Run the tool
   - First scan

2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Overview of what you have
   - What's built (7 stages ✅)
   - Features summary
   - Customization points

3. **[README.md](README.md)** - Full documentation
   - Complete feature list
   - Setup instructions
   - Usage guide
   - API endpoints
   - Database schema
   - Troubleshooting

## 🚀 Getting Started (3 Steps)

1. **Run test setup** (verify installation):
   ```bash
   python test_setup.py
   ```

2. **Start the server**:
   ```bash
   # Mac/Linux
   ./run.sh
   
   # Windows
   run.bat
   ```

3. **Open dashboard**:
   ```
   http://localhost:8000/docs (API)
   dashboard.html (in browser)
   ```

## 🏗️ Architecture

### Backend (Python)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI server with all routes |
| `config.py` | Settings, states, cities, search terms |
| `models.py` | SQLAlchemy database schema |
| `places_api.py` | Google Places API integration |
| `website_auditor.py` | Website analysis & scoring |
| `lead_analyzer.py` | AI-powered lead analysis |
| `deduplicator.py` | Duplicate detection logic |

### Frontend (HTML/JavaScript)

| File | Purpose |
|------|---------|
| `dashboard.html` | Web UI (state selector, scan button, lead table, filters, copy buttons, export) |

### Configuration

| File | Purpose |
|------|---------|
| `.env` | API keys (GOOGLE_PLACES_API_KEY, ANTHROPIC_API_KEY) |
| `.env.example` | Template for .env |
| `requirements.txt` | Python dependencies |

### Startup Scripts

| File | Purpose |
|------|---------|
| `run.sh` | Start script for Mac/Linux |
| `run.bat` | Start script for Windows |
| `test_setup.py` | Verify installation |

### Database

| File | Purpose |
|------|---------|
| `tree_leads.db` | SQLite database (auto-created) |

## 📊 Workflow

```
Select State/City
    ↓
Click Scan
    ↓
API calls Google Places (6 search terms)
    ↓
Fetch & deduplicate results
    ↓
Audit each website (HTTPS, mobile, contact form, etc.)
    ↓
Score website quality (0-100, A-F grades)
    ↓
Analyze with AI (cold opener, pitch, SMS, email, CRM note)
    ↓
Save to database
    ↓
Display in dashboard
    ↓
Filter & copy sales copy
    ↓
Export as CSV
```

## 🎯 Key Concepts

### Lead Priority
- **Call Now** - Hot leads, immediate action
- **Maybe Later** - Warm leads, follow up
- **Skip** - Not a good fit

### Website Grades
- **No Website** - Easiest sell ($500 starter)
- **Broken Website** - Clear pain point ($700 fix)
- **F, D, C** - Poor to okay ($700 redesign)
- **B, A** - Good to great (advanced marketing)

### Sales Opportunity Score
- 0-100 based on:
  - Review count
  - Website quality
  - Offer potential
  - Business category

### AI Analysis Output
For each lead:
- `lead_type` - hot/warm/cold/skip
- `call_priority` - Call Now / Maybe Later / Skip
- `recommended_offer` - Specific offer to pitch
- `main_problem` - What's stopping growth
- `why_this_lead_matters` - 2-3 sentence explanation
- `cold_call_opener` - Direct opening line
- `short_pitch` - 1-2 sentence pitch
- `follow_up_sms` - Text message template
- `follow_up_email` - Email template
- `crm_note` - Internal tracking note

## 📱 Dashboard Features

### Controls
- State selector (SC, NC, GA, expandable)
- City selector (auto-populated)
- Scan button (starts background job)
- Export button (download CSV)
- Status display (shows scan progress)

### Statistics
- Total leads found
- Call Now count
- No website count

### Filters
- All leads
- Call Now priority
- No website
- Broken website
- Grade F
- 50+ reviews

### Lead Table
- Business name, phone, city, rating, grade, priority, score
- Click to expand row and see:
  - Recommended offer
  - Main problem
  - Why this lead matters
  - Cold call opener (copy button)
  - Short pitch (copy button)
  - Follow-up SMS (copy button)
  - Follow-up email (copy button)
  - CRM note (copy button)
  - Business details
  - Date scanned

### Export
- CSV with 19 columns
- Use in CRM, spreadsheet, or email system

## 🔧 Customization

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

### Modify Search Terms
Edit `config.py`:
```python
SEARCH_TERMS = ["tree service", "tree removal", ...]
```

### Adjust Website Audit
Edit `website_auditor.py`, `audit_website()` method:
```python
audit["new_field"] = check_something()
```

### Change AI Prompt
Edit `lead_analyzer.py`, `analyze_lead()` method:
```python
context = f"""
... customize the prompt ...
"""
```

## 📈 Scalability

| Metric | Capacity |
|--------|----------|
| Leads per database | 10,000+ (SQLite handles it) |
| States | Unlimited (add to config) |
| Cities | Unlimited (add to config) |
| Concurrent scans | 1 at a time (sequential) |
| Website audits | ~10s per page (safety timeout) |
| AI analysis | ~2s per lead |

**Scan times:**
- 1 city (average 100 leads): 2-5 minutes
- 10 cities: 20-50 minutes
- 50 cities: 2-5 hours (run overnight)

## 💰 Costs

### API Calls
- **Google Places API**: ~$0.10-0.30 per city scan (depending on results)
- **Anthropic/OpenAI**: ~$0.001-0.002 per lead analyzed

Total cost per city: $0.20-0.50

### Infrastructure
- Server: You run it locally or on any cheap VPS
- Database: SQLite (free, local)
- Storage: <100MB for 1000s of leads

## 🎓 Learning Resources

### Python Files (Self-Documented)
- Each file has docstrings explaining what it does
- Read top-to-bottom for overview
- Check comments for specific logic

### Configuration
- `config.py` shows all available settings
- Modify here to add states, change AI model, adjust search terms

### API Integration
- `places_api.py` shows Google Places API usage
- Can be swapped for other business discovery APIs

### Website Analysis
- `website_auditor.py` shows HTML parsing, feature detection
- Customize to check for specific business elements

### AI Analysis
- `lead_analyzer.py` shows prompt engineering
- Modify prompt to change lead scoring logic

## 🐛 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| "No GOOGLE_PLACES_API_KEY" | Run `python test_setup.py`, add key to .env |
| "Cannot connect to API" | Run `python main.py` first |
| "No results after scan" | Check API key is enabled for Places API |
| "Website audit shows nothing" | Website may be down, check logs |
| "AI analysis empty" | Verify ANTHROPIC_API_KEY, check rate limits |
| "Dashboard won't load" | Open dashboard.html in browser (not localhost) |

## 📞 Support

**Questions?**
1. Read QUICKSTART.md (5 min setup)
2. Read PROJECT_SUMMARY.md (features overview)
3. Read README.md (full docs)
4. Check code comments in Python files
5. Run `python test_setup.py` to verify everything

## ✅ Checklist Before First Scan

- [ ] Copied .env.example to .env
- [ ] Added GOOGLE_PLACES_API_KEY to .env
- [ ] Added ANTHROPIC_API_KEY to .env
- [ ] Ran `pip install -r requirements.txt`
- [ ] Ran `python test_setup.py` (all green)
- [ ] Started `python main.py`
- [ ] Opened dashboard.html in browser
- [ ] Selected state (South Carolina)
- [ ] Selected city (Charleston)
- [ ] Clicked "Scan City" button

## 🎯 Success Metrics

Track these to measure success:

| Metric | Goal |
|--------|------|
| Leads scanned per month | 1000+ (10 cities × 100 leads) |
| Call conversion rate | 5-10% (your calls → meetings) |
| Offer conversion rate | 20-30% (calls → customers) |
| Average deal value | $1000-3000 (initial + recurring) |
| Cost per lead | $0.25 (API costs only) |

**Real example:**
- Scan 10 cities: 1000 leads, cost $2.50
- Call 100 leads at 10% connect rate: 10 meetings
- 2 conversions at 20% rate: 2 customers
- 2 × $1500 = $3000 revenue
- Cost: $2.50
- ROI: 120,000%

---

**Ready?** Start with [QUICKSTART.md](QUICKSTART.md) 🚀
