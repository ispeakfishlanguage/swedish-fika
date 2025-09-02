#!/bin/bash

# Traditional Swedish Fika - Deployment Script
# Deploys application to Digital Ocean App Platform

set -e

echo "🇸🇪 Traditional Swedish Fika - Deployment Script"
echo "================================================"

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI is not installed. Please install it first:"
    echo "   macOS: brew install doctl"
    echo "   Linux: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

if ! doctl auth list &> /dev/null; then
    echo "❌ Digital Ocean authentication required. Please run:"
    echo "   doctl auth init"
    exit 1
fi

echo "✅ Prerequisites checked"

# Configuration
APP_NAME="traditional-swedish-fika"
REGION="nyc3"

echo ""
echo "🔧 Configuration:"
echo "   App Name: $APP_NAME"
echo "   Region: $REGION"
echo ""

# Ask for required environment variables
echo "🔐 Please provide the following environment variables:"
echo ""

read -p "GitHub Username: " GITHUB_USERNAME
read -p "Supabase URL: " SUPABASE_URL
read -s -p "Supabase Anon Key: " SUPABASE_ANON_KEY
echo ""
read -s -p "OpenRouter API Key: " OPENROUTER_API_KEY
echo ""
read -p "Upstash Redis URL: " UPSTASH_REDIS_URL
read -s -p "Upstash Redis Token: " UPSTASH_REDIS_TOKEN
echo ""
read -p "Alert Email: " ALERT_EMAIL

# Update app.yaml with provided values
echo ""
echo "📝 Updating app.yaml configuration..."

sed -i.bak \
    -e "s/YOUR_GITHUB_USERNAME/$GITHUB_USERNAME/g" \
    -e "s/YOUR_EMAIL@example.com/$ALERT_EMAIL/g" \
    .do/app.yaml

echo "✅ Configuration updated"

# Create environment variables file for deployment
cat > .do/envs.yaml << EOF
envs:
  - key: ENVIRONMENT
    value: production
  - key: SUPABASE_URL
    value: $SUPABASE_URL
    type: SECRET
  - key: SUPABASE_ANON_KEY
    value: $SUPABASE_ANON_KEY
    type: SECRET
  - key: OPENROUTER_API_KEY
    value: $OPENROUTER_API_KEY
    type: SECRET
  - key: UPSTASH_REDIS_URL
    value: $UPSTASH_REDIS_URL
    type: SECRET
  - key: UPSTASH_REDIS_TOKEN
    value: $UPSTASH_REDIS_TOKEN
    type: SECRET
EOF

echo ""
echo "🚀 Deploying to Digital Ocean App Platform..."
echo "   This may take 5-10 minutes..."

# Deploy the application
APP_ID=$(doctl apps create --spec .do/app.yaml --format ID --no-header)

if [ $? -eq 0 ]; then
    echo "✅ Application created successfully!"
    echo "   App ID: $APP_ID"
    echo "   App URL: https://$APP_NAME-$APP_ID.ondigitalocean.app"
    echo ""
    
    echo "📊 Monitoring deployment..."
    doctl apps get $APP_ID --format "Name,Status,LiveURL"
    
    echo ""
    echo "🔗 Useful commands:"
    echo "   View app status: doctl apps get $APP_ID"
    echo "   View logs: doctl apps logs $APP_ID --type deploy --follow"
    echo "   Update app: doctl apps update $APP_ID --spec .do/app.yaml"
    echo "   Delete app: doctl apps delete $APP_ID"
    
    # Wait for deployment
    echo ""
    echo "⏳ Waiting for deployment to complete..."
    
    while true; do
        STATUS=$(doctl apps get $APP_ID --format Status --no-header)
        echo "   Status: $STATUS"
        
        if [ "$STATUS" = "ACTIVE" ]; then
            echo "✅ Deployment completed successfully!"
            LIVE_URL=$(doctl apps get $APP_ID --format LiveURL --no-header)
            echo "🌐 Your app is live at: $LIVE_URL"
            break
        elif [ "$STATUS" = "ERROR" ]; then
            echo "❌ Deployment failed. Check logs:"
            echo "   doctl apps logs $APP_ID --type deploy"
            exit 1
        fi
        
        sleep 30
    done
    
    # Clean up sensitive files
    rm -f .do/envs.yaml
    
    echo ""
    echo "🎉 Deployment Complete!"
    echo ""
    echo "🔍 Next Steps:"
    echo "1. Visit your app at: $LIVE_URL"
    echo "2. Check health: $LIVE_URL/health"
    echo "3. View AI dashboard: $LIVE_URL/ai/dashboard"
    echo "4. Monitor logs: doctl apps logs $APP_ID --type run --follow"
    echo ""
    echo "🇸🇪 Happy Fika! Your Swedish Fika Register is now live!"
    
else
    echo "❌ Deployment failed. Please check your configuration and try again."
    exit 1
fi