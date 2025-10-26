# 🚀 Deployment Guide

Complete guide to deploy your AI Summarizer application to various platforms.

---

## 📋 Prerequisites

Before deploying, ensure you have:

1. ✅ Project tested locally
2. ✅ `.env` file configured with API keys
3. ✅ All dependencies in `requirements.txt`
4. ✅ Git repository initialized

---

## 🌐 Option 1: Streamlit Cloud (Recommended - Free & Easy)

### Steps:

1. **Push to GitHub**
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **Deploy to Streamlit Cloud**
   - Go to https://share.streamlit.io/
   - Sign in with GitHub
   - Click "New app"
   - Select your repository: `yourusername/ai-summarizer`
   - Branch: `main`
   - Main file path: `app.py`
   - App URL: `ai-summarizer` (or your choice)

3. **Add Environment Variables**
   - Click "Advanced settings"
   - Add:
     - `GROQ_API_KEY`: Your Groq API key
     - (Optional) `TELEGRAM_BOT_TOKEN`: For bot features

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - Your app is live at: `https://ai-summarizer.streamlit.app`

### Advantages:
- ✅ Completely free
- ✅ Automatic deployments on git push
- ✅ No credit card required
- ✅ HTTPS by default
- ✅ Custom subdomain

---

## 🟣 Option 2: Heroku

### Prerequisites:
- Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli
- Heroku account: https://signup.heroku.com

### Steps:

1. **Login to Heroku**
```bash
heroku login
```

2. **Create Heroku App**
```bash
heroku create ai-summarizer
```

3. **Set Environment Variables**
```bash
heroku config:set GROQ_API_KEY=your_groq_api_key
heroku config:set TELEGRAM_BOT_TOKEN=your_bot_token  # Optional
```

4. **Deploy**
```bash
git push heroku main
```

5. **View Logs**
```bash
heroku logs --tail
```

Your app will be available at: `https://ai-summarizer.herokuapp.com`

---

## ☁️ Option 3: Railway

### Steps:

1. **Sign up**: https://railway.app
2. **Create New Project**
3. **Deploy from GitHub** - Select your repository
4. **Add Environment Variables**:
   - `GROQ_API_KEY`
   - `TELEGRAM_BOT_TOKEN` (optional)
5. **Deploy** - Railway auto-detects Python apps

---

## 🐳 Option 4: Docker Deployment

### Local Docker

```bash
# Build image
docker build -t ai-summarizer .

# Run container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=your_key \
  ai-summarizer

# Or use docker-compose
docker-compose up -d
```

### Docker on Cloud

#### DigitalOcean App Platform:
1. Connect GitHub repository
2. Select Dockerfile
3. Add environment variables
4. Deploy

#### AWS Elastic Beanstalk:
```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p docker

# Create and deploy
eb create ai-summarizer-env
eb deploy
```

---

## 📦 Option 5: VPS Deployment (DigitalOcean, Linode, etc.)

### Steps:

1. **Create VPS** (Ubuntu 20.04+ recommended)
2. **SSH into server**
```bash
ssh root@your-server-ip
```

3. **Install dependencies**
```bash
# Update system
apt update && apt upgrade -y

# Install Python and pip
apt install python3 python3-pip -y

# Install Git
apt install git -y
```

4. **Clone repository**
```bash
git clone https://github.com/yourusername/ai-summarizer.git
cd ai-summarizer
```

5. **Setup virtual environment**
```bash
python3 -m venv botenv
source botenv/bin/activate
pip install -r requirements.txt
```

6. **Setup environment variables**
```bash
nano .env
# Add your API keys
# Save and exit (Ctrl+X, Y, Enter)
```

7. **Install Nginx** (for reverse proxy)
```bash
apt install nginx -y
```

8. **Create systemd service**
```bash
nano /etc/systemd/system/ai-summarizer.service
```

Add:
```ini
[Unit]
Description=AI Summarizer App
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ai-summarizer
Environment="PATH=/root/ai-summarizer/botenv/bin"
ExecStart=/root/ai-summarizer/botenv/bin/streamlit run app.py --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

9. **Start service**
```bash
systemctl daemon-reload
systemctl start ai-summarizer
systemctl enable ai-summarizer
```

10. **Configure Nginx**
```bash
nano /etc/nginx/sites-available/ai-summarizer
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
ln -s /etc/nginx/sites-available/ai-summarizer /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

11. **Setup SSL with Certbot** (optional but recommended)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

---

## 🔐 Environment Variables

Required for all deployments:

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Yes | Groq API key for audio transcription |
| `TELEGRAM_BOT_TOKEN` | No | For Telegram bot functionality |

---

## 📊 Post-Deployment

### Verify Deployment:
1. ✅ App loads without errors
2. ✅ Can upload PDF files
3. ✅ Can paste text for summarization
4. ✅ Audio transcription works (if API key set)
5. ✅ Settings sidebar functions properly

### Monitoring:
- Check application logs
- Monitor resource usage
- Set up uptime monitoring (UptimeRobot, Pingdom)

---

## 🐛 Troubleshooting

### Common Issues:

1. **App crashes on load**
   - Check environment variables
   - Review logs for errors
   - Verify all dependencies installed

2. **PDF upload fails**
   - Check file size limits
   - Verify PyPDF installation

3. **Audio transcription fails**
   - Verify GROQ_API_KEY is set correctly
   - Check API quota/limits

4. **Telegram bot not responding**
   - Verify TELEGRAM_BOT_TOKEN
   - Check bot is running
   - Review webhook settings

---

## 📈 Scaling Considerations

- **Horizontal Scaling**: Deploy multiple instances behind load balancer
- **Caching**: Use Redis for model caching
- **CDN**: Serve static assets via CDN
- **Database**: Store summaries (optional)
- **Monitoring**: Use APM tools (New Relic, DataDog)

---

## 💰 Cost Estimates

- **Streamlit Cloud**: Free
- **Heroku**: Free tier available, $7/month for hobby dyno
- **Railway**: Free tier + pay-as-you-go
- **VPS**: $5-20/month
- **AWS/GCP**: Pay-as-you-go, typically $10-50/month

---

Need help? Open an issue on GitHub!
