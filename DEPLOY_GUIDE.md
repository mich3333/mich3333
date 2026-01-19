# 🚀 Portfolio Deployment Guide

## Quick Deploy to Railway (5 minutes)

Your portfolio is **ready to deploy**! Follow these simple steps:

### Step 1: Sign Up for Railway
1. Go to https://railway.app
2. Click "Login" and sign in with GitHub
3. Authorize Railway to access your repos

### Step 2: Deploy Your Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose repository: **mich3333/mich3333**
4. Choose branch: **claude/setup-memory-system-rlmis**
5. Railway will automatically detect your Procfile and start building

### Step 3: Set Environment Variables (Optional)
In Railway dashboard, go to Variables tab and add:
```
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```
(Skip this if you don't have an API key - portfolio will still work!)

### Step 4: Get Your URL! 🎉
1. After build completes (~2 minutes), go to Settings
2. Click "Generate Domain"
3. Your portfolio will be live at: `https://your-project.railway.app`

---

## Alternative: Deploy to Render

### Quick Steps:
1. Go to https://render.com
2. Sign up with GitHub
3. New → Web Service
4. Connect your repo: **mich3333/mich3333**
5. Configure:
   - **Build Command**: `cd autonomous-claude && pip install -r requirements.txt`
   - **Start Command**: `cd autonomous-claude && python3 web_app.py`
   - **Branch**: `claude/setup-memory-system-rlmis`
6. Click "Create Web Service"
7. Your URL: `https://your-project.onrender.com`

---

## Alternative: Vercel (Static Portfolio Only)

If you want just the portfolio page without backend:

1. Install Vercel CLI: `npm i -g vercel`
2. Run: `vercel --prod`
3. Follow prompts
4. Your URL: `https://your-project.vercel.app`

---

## Your Portfolio URLs Structure

Once deployed, you'll have:
- **Portfolio**: `https://your-site.com/` (main landing page)
- **Dashboard**: `https://your-site.com/dashboard` (interactive dashboard)
- **Showcase**: `https://your-site.com/showcase` (feature showcase)
- **API Status**: `https://your-site.com/api/status`

---

## Troubleshooting

### Build fails?
Make sure requirements.txt exists in `autonomous-claude/` folder.

### Port issues?
web_app.py already configured to use `PORT` env variable automatically.

### Dependencies missing?
Check that Procfile command is: `cd autonomous-claude && python3 web_app.py`

---

## After Deployment ✅

1. Test your live URL
2. Update README.md with your live link
3. Share on LinkedIn/GitHub
4. Add to your resume!

**You're all set!** 🎉
