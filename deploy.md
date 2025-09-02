# Deployment Guide - Traditional Swedish Fika Register

## Prerequisites

1. **Digital Ocean Account** with App Platform access
2. **GitHub Repository** pushed to your account
3. **Supabase Project** set up for production database
4. **Upstash Redis** instance for caching
5. **OpenRouter API Key** for AI functionality

## Step 1: Prepare External Services

### Supabase Setup
1. Create a new project at https://supabase.com
2. Go to Settings > API to get your URL and anon key
3. Run the database schema from `backend/init.sql` in the SQL editor

### Upstash Redis Setup
1. Create account at https://upstash.com
2. Create a new Redis database
3. Note the REST URL and token

### OpenRouter Setup
1. Get API key from https://openrouter.ai
2. Add credits to your account

## Step 2: Deploy to Digital Ocean

### Option A: Using Digital Ocean CLI (Recommended)

1. **Install doctl CLI**
```bash
# macOS
brew install doctl

# Linux
wget https://github.com/digitalocean/doctl/releases/download/v1.98.1/doctl-1.98.1-linux-amd64.tar.gz
tar xf doctl-*.tar.gz
sudo mv doctl /usr/local/bin
```

2. **Authenticate with Digital Ocean**
```bash
doctl auth init
```

3. **Update app.yaml configuration**
   - Edit `.do/app.yaml`
   - Replace `YOUR_GITHUB_USERNAME` with your GitHub username
   - Replace `YOUR_EMAIL@example.com` with your email

4. **Deploy the application**
```bash
cd /Users/carolina/Local\ Sites/fika
doctl apps create --spec .do/app.yaml
```

### Option B: Using Digital Ocean Dashboard

1. **Go to Digital Ocean Dashboard**
   - Navigate to Apps > Create App
   - Choose "GitHub" as source
   - Select your `traditional-swedish-fika` repository

2. **Configure Services**
   
   **Backend Service:**
   - Name: `backend`
   - Source Directory: `/backend`
   - Run Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Environment: Python
   - HTTP Port: 8000
   
   **Frontend Service:**
   - Name: `frontend`
   - Source Directory: `/frontend`
   - Run Command: `python -m http.server 3000 --directory /app`
   - Environment: Python
   - HTTP Port: 3000

3. **Configure Environment Variables**
   Add these as encrypted environment variables:
   ```
   ENVIRONMENT=production
   SUPABASE_URL=your_supabase_url
   SUPABASE_ANON_KEY=your_supabase_anon_key
   OPENROUTER_API_KEY=your_openrouter_key
   UPSTASH_REDIS_URL=your_upstash_url
   UPSTASH_REDIS_TOKEN=your_upstash_token
   ```

4. **Add Database**
   - Add PostgreSQL database component
   - Size: Basic ($7/month)
   - The DATABASE_URL will be auto-configured

## Step 3: Post-Deployment Setup

1. **Initialize Database**
   Once deployed, run database migrations:
   ```bash
   doctl apps logs <app-id> --type run --follow
   ```

2. **Verify Services**
   - Check that all services are running
   - Test the health endpoints
   - Verify database connectivity

3. **Configure DNS (Optional)**
   - Add custom domain in App Platform settings
   - Update DNS records as instructed

## Step 4: Monitoring and Scaling

### Health Checks
- Backend: `https://your-app.ondigitalocean.app/health`
- Metrics: `https://your-app.ondigitalocean.app/metrics`
- AI Dashboard: `https://your-app.ondigitalocean.app/ai/dashboard`

### Scaling
- Monitor CPU/Memory usage in Digital Ocean dashboard
- Scale up instance sizes as needed
- Add load balancing for high traffic

### Logs
```bash
# View application logs
doctl apps logs <app-id> --type build --follow
doctl apps logs <app-id> --type deploy --follow
doctl apps logs <app-id> --type run --follow
```

## Estimated Costs

- **App Platform**: ~$12/month (2 basic services)
- **Managed PostgreSQL**: ~$15/month (basic tier)
- **Supabase**: Free tier (up to 500MB)
- **Upstash Redis**: Free tier (10k commands/day)
- **OpenRouter**: Pay per use (~$0.01-0.10/request)

**Total**: ~$30-40/month for development instance

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all requirements.txt dependencies are correct
   - Verify Python version compatibility
   - Check for missing environment variables

2. **Database Connection Issues**
   - Verify DATABASE_URL is set correctly
   - Check that database migrations ran successfully
   - Ensure Supabase project is active

3. **Redis Connection Issues**
   - Verify Upstash credentials
   - Check Redis URL format
   - Test connection from backend service

4. **AI Service Errors**
   - Verify OpenRouter API key
   - Check available credits
   - Monitor rate limits

### Getting Help

1. **Digital Ocean Support**: Available in dashboard
2. **Logs**: Use `doctl apps logs` command
3. **Health Checks**: Monitor `/health` endpoint
4. **Metrics**: Check Prometheus metrics at `/metrics`

## Security Considerations

1. **Environment Variables**: All secrets stored as encrypted variables
2. **Database**: Managed PostgreSQL with automatic backups
3. **HTTPS**: Automatic SSL certificates
4. **CORS**: Configured for production domains
5. **Rate Limiting**: Implemented in FastAPI middleware

## Performance Optimization

1. **Caching**: Redis configured for API response caching
2. **Database**: Indexed queries for location search
3. **Static Files**: Served efficiently by Digital Ocean
4. **CDN**: Consider adding CDN for global performance

---

🇸🇪 **Happy Fika!** Your Traditional Swedish Fika Register is now deployed and ready to help people discover authentic fika experiences across Sweden.