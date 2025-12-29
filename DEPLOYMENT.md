# 🚀 Deployment Guide

## Deploy to Railway (Recommended - Free!)

Railway provides free hosting perfect for portfolio projects.

### Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Manual Deployment

1. **Sign up for Railway**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Set Environment Variables**
   ```
   OPENAI_API_KEY=your-openai-key-here
   FIGMA_TOKEN=your-figma-token (optional)
   FLASK_ENV=production
   ```

4. **Deploy!**
   - Railway will automatically detect Python
   - Build and deploy
   - Get your live URL: `https://your-app.railway.app`

---

## Deploy to Render (Also Free!)

1. **Sign up**: https://render.com
2. **New Web Service**
3. **Connect GitHub**
4. **Configure:**
   ```
   Build Command: cd autonomous-claude && pip install -r requirements.txt
   Start Command: cd autonomous-claude && python3 web_app.py
   ```
5. **Environment Variables:**
   ```
   OPENAI_API_KEY=your-key
   PORT=10000
   ```

---

## Deploy to Vercel (Frontend Only)

For static portfolio page:

1. Install Vercel CLI:
   ```bash
   npm i -g vercel
   ```

2. Deploy:
   ```bash
   vercel
   ```

---

## Deploy to Fly.io

1. **Install flyctl**:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**:
   ```bash
   fly auth login
   ```

3. **Launch**:
   ```bash
   fly launch
   ```

4. **Set secrets**:
   ```bash
   fly secrets set OPENAI_API_KEY=your-key
   ```

5. **Deploy**:
   ```bash
   fly deploy
   ```

---

## Environment Variables

### Required:
- `OPENAI_API_KEY` - Your OpenAI API key
- `PORT` - Port number (set automatically by hosting)

### Optional:
- `FIGMA_TOKEN` - Figma Personal Access Token
- `FLASK_ENV` - Set to `production` for deployed version

---

## Post-Deployment Checklist

✅ Test all pages:
- [ ] Portfolio: `https://your-app.com/`
- [ ] Dashboard: `https://your-app.com/dashboard`
- [ ] Showcase: `https://your-app.com/showcase`
- [ ] API: `https://your-app.com/api/status`

✅ Set environment variables:
- [ ] OPENAI_API_KEY
- [ ] FLASK_ENV=production

✅ Test features:
- [ ] Memory system works
- [ ] ChatGPT integration works
- [ ] Dashboard updates in real-time

✅ Update README:
- [ ] Add live demo URL
- [ ] Update deployment badge

---

## Troubleshooting

### App not starting?
Check logs:
```bash
# Railway
railway logs

# Render
Check dashboard logs

# Fly.io
fly logs
```

### Database issues?
Make sure data directory is writable:
```bash
mkdir -p autonomous-claude/data/memory
chmod 755 autonomous-claude/data
```

### Missing dependencies?
Verify requirements.txt is complete:
```bash
pip install -r autonomous-claude/requirements.txt
```

---

## Cost Estimate

| Platform | Free Tier | Cost After |
|----------|-----------|------------|
| Railway | $5/month free credit | $0.000231/min |
| Render | 750 hours/month | $7/month |
| Fly.io | 3 VMs free | ~$2/month |
| Vercel | Unlimited (static) | Free |

**Recommendation**: Railway for full app, Vercel for portfolio page only.

---

## Custom Domain

### Railway:
1. Go to project settings
2. Click "Domains"
3. Add custom domain
4. Update DNS records

### Render:
1. Go to settings
2. Add custom domain
3. Configure DNS

---

## SSL Certificate

All platforms provide free SSL automatically! 🔒

---

## Monitoring

### Railway Dashboard
- View logs
- Check metrics
- Monitor usage

### Add Analytics (Optional)
```html
<!-- Add to templates/base.html -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>
```

---

## Update After Deployment

README.md:
```markdown
## 🌐 Live Demo

**[View Live Demo](https://your-app.railway.app)** 🚀

Try it yourself:
- Portfolio: https://your-app.railway.app/
- Dashboard: https://your-app.railway.app/dashboard
- API Docs: https://your-app.railway.app/api/status
```

Resume/CV:
```
GitHub: github.com/yourname/autonomous-claude
Live Demo: https://your-app.railway.app
```

---

## Next Steps After Deployment

1. ✅ Add live URL to README
2. ✅ Add deployment badge
3. ✅ Test all features
4. ✅ Share on LinkedIn/Twitter
5. ✅ Add to resume
6. ✅ Send to recruiters!

**Your project is now live! 🎉**
