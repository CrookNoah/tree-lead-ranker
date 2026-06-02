# Tree Lead Ranker - Deployment Guide

Deploy Tree Lead Ranker to production for continuous lead generation.

## Local Development

### Quick Start
```bash
./run.sh        # Mac/Linux
run.bat         # Windows
```

Server runs on `http://localhost:8000`

## Deployment Options

### Option 1: VPS (Recommended for Production)

**Providers:** DigitalOcean, Linode, Vultr, AWS EC2 (~$5-15/month)

**Setup:**

```bash
# SSH into server
ssh root@your_server_ip

# Install Python
apt update && apt install -y python3 python3-pip python3-venv

# Clone repository
git clone <your-repo> tree-lead-ranker
cd tree-lead-ranker

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure
nano .env  # Add API keys

# Test
python test_setup.py

# Run with Supervisor or PM2 (keep running)
```

### Option 2: Docker

**Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

**Build & Run:**

```bash
docker build -t tree-lead-ranker .
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/tree_leads.db:/app/tree_leads.db \
  -e GOOGLE_PLACES_API_KEY=$GOOGLE_PLACES_API_KEY \
  -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
  tree-lead-ranker
```

### Option 3: Heroku

**Procfile:**

```
web: python main.py
```

**Deploy:**

```bash
heroku create tree-lead-ranker
heroku config:set GOOGLE_PLACES_API_KEY=...
heroku config:set ANTHROPIC_API_KEY=...
git push heroku main
```

Note: Heroku's ephemeral filesystem means database resets on restart. Use PostgreSQL add-on instead.

### Option 4: Render / Railway / Fly.io

Similar to Heroku - simple GitHub integration, follow their Python deployment guides.

## Production Considerations

### Database Persistence

**Option A: SQLite (Simple, for < 10k leads)**
```python
# models.py is already configured for SQLite
# Backup regularly:
cp tree_leads.db tree_leads.backup.$(date +%Y%m%d).db
```

**Option B: PostgreSQL (Better for scaling)**

```bash
# Install postgres driver
pip install psycopg2-binary

# Update models.py
DATABASE_URL = "postgresql://user:password@localhost/tree_leads"
```

### Background Jobs

For longer scans, use a task queue:

**Option A: Celery (Production-grade)**

```bash
pip install celery redis
```

```python
# main.py
from celery import Celery

celery = Celery(__name__)

@app.post("/scan")
async def scan_city(request: ScanRequest):
    # Start async task
    perform_scan.delay(request.state, request.city, ...)
    return {"status": "Scanning..."}

@celery.task
def perform_scan(state, city, state_name):
    # ... existing scan logic
    pass
```

**Option B: RQ (Redis Queue, lighter weight)**

```bash
pip install rq
```

**Option C: APScheduler (Keep it simple)**

```bash
pip install APScheduler
```

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(func=daily_rescan, trigger="cron", hour=2)
scheduler.start()
```

### Web Server (Production)

Don't run FastAPI directly. Use a proper ASGI server:

**Gunicorn + Uvicorn:**

```bash
pip install gunicorn

# Run
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

**Supervisor config** (`/etc/supervisor/conf.d/tree-lead-ranker.conf`):

```ini
[program:tree-lead-ranker]
directory=/home/ubuntu/tree-lead-ranker
command=/home/ubuntu/tree-lead-ranker/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    main:app \
    --bind 0.0.0.0:8000
autostart=true
autorestart=true
stderr_logfile=/var/log/tree-lead-ranker.err.log
stdout_logfile=/var/log/tree-lead-ranker.out.log
```

**Start:**

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start tree-lead-ranker
```

### Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name tree-leads.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/HTTPS

**Let's Encrypt (Free):**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --standalone -d tree-leads.yourdomain.com
```

### Monitoring

**Option A: PM2 (Simple process manager)**

```bash
npm install -g pm2

pm2 start main.py --name "tree-lead-ranker" --interpreter python3
pm2 monit
```

**Option B: CloudFlare / Uptime Robot (Monitoring)**

- Ping `/` endpoint every 5 minutes
- Alert if server is down

**Option C: Logs**

```bash
# Check logs
tail -f /var/log/tree-lead-ranker.out.log
```

### Rate Limits & Throttling

**Protect API endpoints:**

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/scan")
@limiter.limit("5/minute")
async def scan_city(request: ScanRequest):
    # ...
```

### Backup Strategy

```bash
# Daily backup to S3
0 2 * * * aws s3 cp tree_leads.db s3://my-bucket/backups/tree_leads.$(date +\%Y\%m\%d).db
```

Or use `zip`:

```bash
0 2 * * * cd /app && zip -q backups/tree_leads.$(date +%Y%m%d).zip tree_leads.db
```

### Environment Variables

```bash
# .env on production server
GOOGLE_PLACES_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
DATABASE_URL=postgresql://...  # if using postgres
AI_MODEL=anthropic
ENVIRONMENT=production
```

### Logging

```python
# Add to main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tree-lead-ranker.log'),
        logging.StreamHandler()
    ]
)
```

## Scheduled Rescans

Run scans automatically on a schedule:

**Option A: Cron Job**

```bash
# Rescan all SC cities every Sunday at 2am
0 2 * * 0 cd /home/ubuntu/tree-lead-ranker && python3 rescan.py SC
```

**Create `rescan.py`:**

```python
import sys
from main import perform_scan
from config import STATES_AND_CITIES

if __name__ == "__main__":
    state = sys.argv[1] if len(sys.argv) > 1 else "SC"
    state_data = STATES_AND_CITIES[state]
    
    for city in state_data["cities"]:
        print(f"Scanning {city}...")
        perform_scan(state, city, state_data["state_name"])
        print(f"✅ {city} complete")
```

**Option B: APScheduler**

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def rescan_all_cities():
    for state_code, state_data in STATES_AND_CITIES.items():
        for city in state_data["cities"]:
            perform_scan(state_code, city, state_data["state_name"])

# Rescan at 2am every Sunday
scheduler.add_job(rescan_all_cities, trigger="cron", day_of_week=6, hour=2)
scheduler.start()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Deployment Checklist

- [ ] Server provisioned (VPS, Docker, or PaaS)
- [ ] Python 3.9+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env configured with API keys
- [ ] `test_setup.py` passes
- [ ] WSGI server configured (Gunicorn)
- [ ] Reverse proxy configured (Nginx)
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] Database backed up
- [ ] Monitoring configured
- [ ] Logging configured
- [ ] Backup schedule set
- [ ] Rescan schedule set
- [ ] Tests passing

## Quick Deploy to DigitalOcean

```bash
# 1. Create droplet (Ubuntu 22.04, Basic $4/month)
# 2. SSH in
ssh root@your_ip

# 3. Setup
apt update && apt install -y python3 python3-pip python3-venv git
git clone <your-repo> tree-lead-ranker
cd tree-lead-ranker

# 4. Configure
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano .env  # Add API keys

# 5. Test
python test_setup.py

# 6. Install supervisor
apt install -y supervisor

# 7. Create supervisor config
cat > /etc/supervisor/conf.d/tree-lead-ranker.conf << 'EOF'
[program:tree-lead-ranker]
directory=/root/tree-lead-ranker
command=/root/tree-lead-ranker/venv/bin/gunicorn \
    -w 4 \
    -k uvicorn.workers.UvicornWorker \
    main:app \
    --bind 127.0.0.1:8000
autostart=true
autorestart=true
EOF

# 8. Start service
supervisorctl reread && supervisorctl update && supervisorctl start tree-lead-ranker

# 9. Install nginx
apt install -y nginx

# 10. Configure nginx
nano /etc/nginx/sites-available/default
# Add proxy_pass http://127.0.0.1:8000;

# 11. Restart nginx
systemctl restart nginx

# Done! Access at http://your_ip
```

## Monitoring Dashboard

Create a simple status page:

```python
# Add to main.py
@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.query(Business).count()
        db.close()
        return {"status": "healthy", "db": "connected"}
    except:
        return {"status": "unhealthy", "db": "disconnected"}, 500
```

## Cost Estimate

| Component | Cost |
|-----------|------|
| VPS (Digital Ocean basic) | $5/mo |
| Domain name | $10/year |
| SSL (Let's Encrypt) | Free |
| Google Places API | $0.20-0.50/scan |
| Anthropic API | $0.001/lead |

**Monthly cost:** $5 + API calls = ~$10-20/mo

## Support

Check logs when issues occur:

```bash
# Server logs
tail -f /var/log/tree-lead-ranker.out.log

# Nginx logs
tail -f /var/log/nginx/error.log

# Database status
sqlite3 tree_leads.db "SELECT COUNT(*) FROM businesses;"
```

---

**Need help?** Start with a simple VPS deployment, add complexity as you scale. 🚀
