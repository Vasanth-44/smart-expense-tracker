# Vercel Deployment Guide

## Quick Deploy Steps

### 1. Install Vercel CLI (Optional)
```bash
npm install -g vercel
```

### 2. Deploy via Vercel Dashboard (Recommended)

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "Add New Project"
3. Import your GitHub repository: `Vasanth-44/smart-expense-tracker`
4. Configure project:
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`
   - **Install Command**: `npm install`

5. Add Environment Variables (if needed):
   - `REACT_APP_API_URL`: Your backend API URL

6. Click "Deploy"

### 3. Deploy via CLI (Alternative)

```bash
# Login to Vercel
vercel login

# Deploy from project root
cd frontend
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? smart-expense-tracker
# - Directory? ./
# - Override settings? No
```

## Backend Deployment

**Note**: Vercel has limitations for Python backends with databases. For the backend, consider:

### Option 1: Deploy Backend to Render (Recommended)
1. Go to [render.com](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3

### Option 2: Deploy Backend to Railway
1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub repo
3. Configure root directory to `backend`
4. Add environment variables

### Option 3: Keep Backend Local (Development Only)
- Use ngrok to expose local backend: `ngrok http 8000`
- Update frontend API URL to ngrok URL

## Update Frontend API URL

After deploying backend, update the API URL in your frontend:

**File**: `frontend/src/services/api.js`

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'https://your-backend-url.com';
```

Then add environment variable in Vercel dashboard:
- Key: `REACT_APP_API_URL`
- Value: `https://your-backend-url.com`

## Auto-Deploy on Push

Once connected to GitHub, Vercel automatically deploys when you:
1. Push to main branch
2. Merge a pull request

## Custom Domain (Optional)

1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

## Troubleshooting

### Build Fails
- Check build logs in Vercel dashboard
- Ensure all dependencies are in package.json
- Verify Node version compatibility

### API Connection Issues
- Verify REACT_APP_API_URL is set correctly
- Check CORS settings in backend
- Ensure backend is deployed and running

### Environment Variables
- Add all required env vars in Vercel dashboard
- Prefix React env vars with `REACT_APP_`
- Redeploy after adding env vars

## Post-Deployment

Your app will be available at:
- `https://your-project-name.vercel.app`
- Or your custom domain

## Making Changes After Deployment

1. Make changes locally
2. Test locally
3. Commit: `git add . && git commit -m "your message"`
4. Push: `git push origin main`
5. Vercel auto-deploys (takes 1-2 minutes)
