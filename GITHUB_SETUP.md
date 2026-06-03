# 🚀 Push to GitHub

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository:
   - **Name:** `tree-lead-ranker`
   - **Description:** Professional lead generation system for tree service companies
   - **Public** (so you can clone anywhere)
   - **Don't initialize** with README (we already have one)
   - Click **Create repository**

## Step 2: Connect & Push

After creating the repo, GitHub will show you commands. **Run these on your computer:**

```bash
cd tree-lead-ranker
git remote add origin https://github.com/YOUR_USERNAME/tree-lead-ranker.git
git branch -M main
git push -u origin main
```

(Replace `YOUR_USERNAME` with your actual GitHub username)

## Step 3: Clone on Your VPS

Once pushed, SSH into your Hostinger VPS and run:

```bash
apt update
apt install -y python3-pip git
cd /opt
git clone https://github.com/YOUR_USERNAME/tree-lead-ranker.git
cd tree-lead-ranker
pip3 install -r requirements.txt
python3 -m uvicorn main:app --host 0.0.0.0 --port 3000
```

Then open:
```
http://2.24.120.111:3000/dashboard_v2.html
```

---

## Complete! 

Your app is:
- ✅ On GitHub (backed up, shareable)
- ✅ Running on your VPS
- ✅ Accessible from anywhere

**One-liner for VPS:**
```bash
git clone https://github.com/YOUR_USERNAME/tree-lead-ranker.git && cd tree-lead-ranker && pip3 install -r requirements.txt && python3 -m uvicorn main:app --host 0.0.0.0 --port 3000
```
