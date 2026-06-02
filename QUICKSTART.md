# Tree Lead Ranker - Quick Start Guide

## 5-Minute Setup

### Step 1: Get API Keys (5 min)

**Google Places API:**
1. Visit https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable "Places API" and "Maps JavaScript API"
4. Go to Credentials → Create API Key
5. Copy the API key

**Anthropic API (for AI analysis):**
1. Visit https://console.anthropic.com/
2. Create API key
3. Copy it

### Step 2: Configure (1 min)

**On Mac/Linux:**
```bash
cd tree-lead-ranker
cp .env.example .env
nano .env
# Paste your API keys
```

**On Windows:**
```bash
cd tree-lead-ranker
copy .env.example .env
notepad .env
# Paste your API keys
```

### Step 3: Install & Run (3 min)

**Mac/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**Windows:**
```bash
run.bat
```

This will:
- Create Python virtual environment
- Install dependencies
- Validate API keys
- Start the server

### Step 4: Open Dashboard

```
http://localhost:8000/docs  (API docs)
```

Or open `dashboard.html` in your browser.

## First Scan

1. **Select State:** South Carolina
2. **Select City:** Charleston
3. **Click "🔍 Scan City"**
4. Wait ~2-5 minutes for scan to complete
5. View results in the dashboard
6. Click rows to expand details
7. Use copy buttons for openers, SMS, email
8. Export CSV when done

## What You'll See

**Lead Priority Badges:**
- 🔴 **Call Now** - Hot leads, immediate action
- 🟠 **Maybe Later** - Warm leads, follow up later
- ⚪ **Skip** - Not a good fit

**Website Grades:**
- **No Website** - They need a $500 starter site
- **Broken Website** - They need a $700 fix
- **F, D, C** - They need a $700 redesign
- **B, A** - They need advanced marketing

**Filters:**
- **Call Now** - See hot leads
- **No Website** - Easiest sell ($500 starter site)
- **Broken Website** - Second easiest ($700 repair)
- **Grade F** - Worst websites ($700 redesign)
- **50+ Reviews** - Busy, established companies

## Sales Process

1. **Read the cold call opener** → Copy it
2. **Call the business** using the phone number
3. **Use the short pitch** if they ask what you're calling about
4. **Send follow-up SMS** after (from the template)
5. **Send follow-up email** next day
6. **Add CRM note** to your system

## Common Questions

**Q: How long does a scan take?**
A: 2-5 minutes per city depending on internet speed.

**Q: Can I scan multiple cities?**
A: Yes, one at a time. Scan all cities in a state, then export one CSV.

**Q: What if API key fails?**
A: Check that Google Places API is enabled in Cloud Console. Verify key has no restrictions.

**Q: Why are some results duplicates?**
A: The tool automatically deduplicates by phone, domain, and name. Duplicates are hidden in the dashboard.

**Q: Can I customize the sales pitch?**
A: Yes, edit the `lead_analyzer.py` file to change the AI prompt or manually edit CSV after export.

**Q: How often should I re-scan?**
A: Re-scan every 3-6 months to find new leads and updated information.

## Next Steps

1. **Scan all cities in South Carolina** (10-15 cities)
2. **Filter for "Call Now" leads**
3. **Use the copy buttons** to get openers and pitches
4. **Make calls and track responses** (which offers convert?)
5. **Export to CSV** and load into your CRM
6. **Run email/SMS sequences** from the templates
7. **Repeat monthly/quarterly** to refresh leads

## Troubleshooting

**"Cannot connect to API"**
- Make sure server is running: `python main.py`
- Check http://localhost:8000

**"No results after scan"**
- Check console for errors
- Verify API key is correct and enabled
- Try a different city

**"AI analysis not working"**
- Verify ANTHROPIC_API_KEY in .env
- Check rate limits (wait 5 min between heavy use)
- Try using OpenAI instead (set in .env)

**"Website audit shows nothing"**
- Website may be down or very slow
- Increase timeout in website_auditor.py
- Some sites block bots - that's okay, skip them

## File Structure

```
tree-lead-ranker/
├── run.sh / run.bat          ← Start here!
├── dashboard.html            ← Open in browser
├── main.py                   ← FastAPI backend
├── config.py                 ← Settings & state/cities
├── models.py                 ← Database schema
├── places_api.py             ← Google Places
├── website_auditor.py        ← Website analysis
├── lead_analyzer.py          ← AI scoring
├── deduplicator.py           ← Duplicate detection
├── .env                      ← Your API keys (create from .env.example)
├── tree_leads.db             ← SQLite database (auto-created)
└── tree_leads_SC.csv         ← Export (auto-created)
```

## Key Metrics

**Website Quality Score (0-100):**
- 90+ = Grade A (fully optimized)
- 80-89 = Grade B (good website)
- 70-79 = Grade C (okay website)
- 60-69 = Grade D (poor website)
- <60 = Grade F (very poor)

**Sales Opportunity Score (0-100):**
- 80+ = Hot lead (high conversion potential)
- 60-79 = Warm lead (good potential)
- 40-59 = Cold lead (lower potential)
- <40 = Skip (not a good fit)

## Your Offers

| Problem | Offer | Price |
|---------|-------|-------|
| No website | Starter website + hosting | $500 + $99/mo |
| Broken website | Fix/rebuild + hosting | $700 + $99/mo |
| Bad website | Redesign + hosting | $700 + $99/mo |
| Okay website | Local SEO pages + extras | Custom |
| Good website | Advanced marketing suite | Custom |

## Success Tips

1. **Focus on "Call Now" leads first** - They're easiest to close
2. **No website + 50+ reviews = EXTREMELY hot** - They're leaving money on the table
3. **Use the copy buttons** - Don't improvise the pitch
4. **Call same day you scan** - Freshness matters
5. **Track what works** - Which offers convert? Repeat those
6. **Re-scan quarterly** - New leads keep coming
7. **Ask for referrals** - Happy customers lead to more customers

---

**Ready? Run the script, scan a city, make some calls!** 🚀

Questions? Check README.md for full docs.
