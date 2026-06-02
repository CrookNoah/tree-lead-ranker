# 🚀 Tree Lead Ranker is LIVE

## Quick Links

### Local Access (On Your Computer)
- **Dashboard**: http://localhost:8000/dashboard_v2.html
- **API Docs**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

### From This Machine
- **Dashboard**: http://10.0.0.198:8000/dashboard_v2.html
- **API Docs**: http://10.0.0.198:8000/docs

## Server Status
✅ **Running** on port 8000
✅ **API responding** 
✅ **Dashboard available**
✅ **Database initialized**

## First Time Setup

1. **Open Dashboard**
   ```
   http://localhost:8000/dashboard_v2.html
   ```

2. **Add Google Places API Key**
   - Edit `.env` file
   - Add: `GOOGLE_PLACES_API_KEY=your_key_here`
   - Restart server

3. **Select State & City**
   - Choose state from dropdown
   - Choose city from dropdown
   - Click "Scan City"

4. **Track Leads**
   - Log calls
   - Tag leads
   - View analytics
   - Export CSV

## Commands

**Check if running:**
```bash
ps aux | grep uvicorn
```

**Stop server:**
```bash
kill $(cat server.pid)
```

**Restart server:**
```bash
pkill -f uvicorn
cd /data/.openclaw/workspace/tree-lead-ranker
/data/.local/bin/uvicorn main:app --host 0.0.0.0 --port 8000 &
```

**View logs:**
```bash
tail -f server.log
```

## API Endpoints

- `GET /states` - List all states
- `GET /states/{state}/cities` - List cities in state
- `POST /scan` - Start city scan
- `GET /leads` - Get all leads
- `GET /leads/{id}` - Get lead details
- `POST /leads/{id}/call-log` - Log a call
- `POST /leads/{id}/tag` - Add tag
- `GET /stats` - Get statistics
- `GET /export/csv` - Export CSV

## API Documentation

Full interactive docs at:
```
http://localhost:8000/docs
```

This shows all endpoints, request/response formats, and lets you test directly.

## Database

SQLite database stored at:
```
tree_leads.db
```

Contains:
- Business info (name, phone, address, website)
- Website audit results
- Behavioral scores
- Decision-maker intel
- Financial ROI data
- Call logs
- Lead tags

## Troubleshooting

**Server won't start?**
1. Check port 8000 is free: `lsof -i :8000`
2. Kill existing process: `pkill -f uvicorn`
3. Check logs: `cat server.log`

**API not responding?**
1. Verify server running: `ps aux | grep uvicorn`
2. Check endpoint: `curl http://localhost:8000/docs`
3. View logs: `tail -f server.log`

**Dashboard not loading?**
1. Check API is running
2. Try refreshing browser (Ctrl+F5)
3. Open http://localhost:8000/docs to verify API

**No leads appearing?**
1. Add Google Places API key to `.env`
2. Click "Scan City" button
3. Wait 2-5 minutes (first scan is slow)
4. Check browser console for errors (F12)

## Configuration

Edit `.env` file:
```
DATABASE_URL=sqlite:///./tree_leads.db
GOOGLE_PLACES_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
TWILIO_ACCOUNT_SID=optional
TWILIO_AUTH_TOKEN=optional
```

Restart server after changes.

## Features Enabled

✅ Lead discovery (Google Places API)
✅ Website auditing (13-point check)
✅ Behavioral scoring
✅ Decision-maker finding
✅ ROI calculation
✅ Call logging
✅ Lead tagging
✅ Dark mode
✅ Mobile responsive
✅ CSV export
✅ Analytics

## Ready?

1. Open: **http://localhost:8000/dashboard_v2.html**
2. Get Google Places API key
3. Add key to `.env`
4. Start scanning!

Questions? Check logs:
```bash
tail -f server.log
```

---

**Server PID**: 15352
**Port**: 8000
**Database**: tree_leads.db
**Start Time**: Running now
