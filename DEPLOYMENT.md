# 🚀 PCTE Helpdesk Chatbot - Free Deployment Guide

## 📋 Prerequisites
- GitHub account (free)
- Vercel account (free) - for frontend
- Railway account (free) - for backend

## 🎯 Quick Deploy Options

### Option 1: Vercel + Railway (Recommended)

#### Backend Deployment (Railway)
1. Go to [railway.app](https://railway.app) and sign up with GitHub
2. Click "Start a new Project" → "Deploy from GitHub repo"
3. Select your chatbot repository
4. Choose the `chatbot` folder as the service
5. Add environment variables:
   - `GOOGLE_API_KEY` = your_gemini_api_key
   - `FLASK_ENV` = production
6. Deploy! You'll get a URL like: `https://your-app.railway.app`

#### Frontend Deployment (Vercel)
1. Go to [vercel.com](https://vercel.com) and sign up with GitHub
2. Click "New Project" → Import your repository
3. Set Root Directory to `front-end`
4. Update environment variables (if needed)
5. Deploy! You'll get a URL like: `https://your-app.vercel.app`

#### Connect Frontend to Backend
Update the API URL in your frontend:
- In `front-end/src/hooks/useChatbot.ts`
- Change `http://localhost:8000/chat` to `https://your-railway-app.railway.app/chat`

### Option 2: Alternative Free Options

#### Netlify (Frontend)
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop your `front-end/dist` folder after building
3. Or connect to GitHub for automatic deployments

#### Render (Backend)
1. Go to [render.com](https://render.com)
2. Create new Web Service from GitHub
3. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python api_server.py`

## 🔧 Build Commands

### Frontend Build
```bash
cd front-end
npm install
npm run build
```

### Backend Requirements
Make sure your `requirements.txt` includes all dependencies:
- flask>=2.3.0
- flask-cors>=4.0.0
- google-generativeai>=0.3.0
- torch>=2.0.0
- nltk>=3.8.0
- numpy>=1.24.0
- requests>=2.31.0
- python-dotenv>=1.0.0

## 🌐 Final URLs
After deployment, you'll have:
- **Frontend**: https://your-chatbot.vercel.app
- **Backend API**: https://your-api.railway.app
- **Your chatbot will be live and accessible worldwide!**

## 🔒 Security Notes
- Never commit your `.env` file with API keys
- Use environment variables on the deployment platforms
- Enable CORS properly for your frontend domain

## 💡 Cost
- **Vercel**: Free tier includes 100GB bandwidth
- **Railway**: Free tier includes 500 hours/month
- **Total Cost**: $0/month for personal projects!