# Traditional Swedish Fika Register - Technical Implementation

## Project Overview

A comprehensive web application for discovering traditional Swedish fika locations across Sweden's major cities, built with a modern tech stack featuring AI-powered recommendations and robust caching.

## Architecture Overview

```
Frontend (Public/SEO-Friendly)
├── Static HTML/CSS/JS
├── Google Indexable
└── Quick navigation to major cities

Backend (Private/AI-Powered)
├── FastAPI Python Server
├── AI Dashboard (/ai/dashboard)
├── Protected routes
└── API endpoints
```

## Technology Stack

### Core Technologies
- **Backend**: Python FastAPI
- **Frontend**: HTML/CSS/JavaScript (Vanilla)
- **Database**: Supabase (Production) / SQLite (Development)
- **Caching**: Redis via Upstash
- **AI Framework**: LangChain
- **LLM Provider**: OpenRouter
- **Containerization**: Docker
- **Deployment**: Digital Ocean
- **Version Control**: GitHub

### Development Environment
- Docker Compose for local development
- Hot reload for both frontend and backend
- Database migrations via Alembic
- Redis for session management and caching

## Database Schema

### Core Tables

#### Places Table
```sql
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    address VARCHAR(500),
    city VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    phone VARCHAR(50),
    website VARCHAR(255),
    opening_hours JSONB,
    fika_specialties TEXT[],
    price_range INTEGER CHECK (price_range >= 1 AND price_range <= 4),
    rating DECIMAL(3, 2),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Reviews Table
```sql
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    user_name VARCHAR(100),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    fika_items TEXT[],
    visit_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Categories Table
```sql
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50)
);
```

#### Place Categories Junction Table
```sql
CREATE TABLE place_categories (
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    category_id UUID REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (place_id, category_id)
);
```

### Indexes for Performance
```sql
-- Geographic search optimization
CREATE INDEX idx_places_location ON places USING GIN (geography(point(longitude, latitude)));

-- City-based searches
CREATE INDEX idx_places_city ON places(city);

-- Rating and verification filters
CREATE INDEX idx_places_rating ON places(rating DESC) WHERE verified = TRUE;

-- Full-text search
CREATE INDEX idx_places_fts ON places USING gin(to_tsvector('english', name || ' ' || description));
```

## Swedish Fika Locations Database

### Major Cities Coverage

#### Stockholm (Capital - Population: ~975,000)
- **Traditional Konditoris**: Vete-Katten (1928), Café Pascal, Rosendals Trädgård
- **Modern Fika Spots**: Drop Coffee, Johan & Nyström, Café String
- **Specialty Items**: Princess cake, kanelbullar, kardemummabullar

#### Gothenburg (Population: ~580,000)  
- **Historic Cafés**: Café Husaren (famous for giant cinnamon buns), Café Kringlan
- **Haga District**: Traditional wooden house cafés
- **Specialty**: Enormous cinnamon buns, local pastries

#### Malmö (Population: ~350,000)
- **Cultural Mix**: Swedish-Danish fusion fika culture
- **Notable Spots**: Lilla Kafferosteriet, Café Slottsträdgården
- **Specialty**: International pastries with Swedish twist

#### Uppsala (Population: ~230,000)
- **University Town**: Student-friendly fika culture
- **Historic Venues**: Guntherska Hovkonditori, Café Linnéan
- **Academic Atmosphere**: Study-friendly environments

#### Västerås (Population: ~155,000)
- **Industrial Heritage**: Worker café traditions
- **Local Favorites**: Traditional Swedish pastries
- **Community Focus**: Neighborhood konditoris

### Traditional Fika Elements Database

#### Classic Pastries
```json
{
  "kanelbulle": {
    "name": "Cinnamon Bun",
    "description": "Spiral-shaped bun with cinnamon and pearl sugar",
    "traditional": true,
    "popularity": "national_symbol"
  },
  "prinsesstårta": {
    "name": "Princess Cake",
    "description": "Sponge cake with pastry cream and green marzipan",
    "traditional": true,
    "difficulty": "high"
  },
  "mazarin": {
    "name": "Mazarin",
    "description": "Small almond tart covered with thin icing",
    "traditional": true,
    "size": "individual"
  },
  "vaniljhjärta": {
    "name": "Vanilla Heart",
    "description": "Heart-shaped pastry with vanilla cream",
    "traditional": true,
    "shape": "heart"
  }
}
```

## API Architecture

### Public Frontend Routes (SEO-Friendly)
```
GET /                           # Homepage
GET /stockholm                  # Stockholm fika locations
GET /gothenburg                # Gothenburg fika locations  
GET /malmo                     # Malmö fika locations
GET /uppsala                   # Uppsala fika locations
GET /vasteras                  # Västerås fika locations
GET /search?q=<query>          # Search locations
GET /place/<id>                # Individual place details
```

### Private Backend API Routes
```
/ai/dashboard                   # AI-powered admin dashboard
/ai/api/places                 # CRUD operations for places
/ai/api/places/<id>            # Individual place management
/ai/api/reviews                # Review management
/ai/api/analytics              # Usage analytics
/ai/api/recommendations        # AI-powered recommendations
/ai/api/import                 # Bulk data import
/ai/api/moderate               # Content moderation
```

### AI-Powered Features

#### LangChain Integration
```python
# AI Agents for different tasks
class FikaRecommendationAgent:
    """Recommends fika spots based on user preferences"""
    
class ContentModerationAgent:
    """Moderates user reviews and content"""
    
class LocationEnrichmentAgent:
    """Enriches location data with additional information"""
```

#### OpenRouter LLM Integration
```python
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

# Configure OpenRouter endpoint
llm = ChatOpenAI(
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key="YOUR_OPENROUTER_API_KEY",
    model_name="anthropic/claude-3-haiku"
)
```

## FastAPI Backend Structure

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── user.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── place.py
│   │   └── review.py
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── places.py
│   │   ├── reviews.py
│   │   └── ai.py
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── place_service.py
│   │   ├── ai_service.py
│   │   └── cache_service.py
│   ├── ai/                     # AI-related modules
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── recommendations.py
│   │   └── moderation.py
│   └── utils/                  # Utility functions
│       ├── __init__.py
│       ├── geo.py
│       └── validators.py
├── alembic/                    # Database migrations
├── tests/
├── requirements.txt
└── Dockerfile
```

### Key FastAPI Features
```python
# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis

app = FastAPI(
    title="Swedish Fika Register API",
    description="API for discovering traditional Swedish fika locations",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Redis caching
@app.on_event("startup")
async def startup():
    redis_client = redis.from_url(
        "redis://redis:6379", encoding="utf-8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fika-cache")
```

## Redis Caching Strategy

### Cache Keys Structure
```
fika:places:{city}                    # Places by city (TTL: 1 hour)
fika:place:{id}                       # Individual place (TTL: 4 hours)
fika:search:{query_hash}              # Search results (TTL: 30 minutes)
fika:recommendations:{user_hash}      # AI recommendations (TTL: 1 hour)
fika:reviews:{place_id}              # Place reviews (TTL: 2 hours)
```

### Caching Implementation
```python
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache

@cache(expire=3600)  # 1 hour
async def get_places_by_city(city: str):
    """Cached function to get places by city"""
    return await database.fetch_places_by_city(city)

@cache(expire=1800, key_builder=lambda *args, **kwargs: f"search:{hash(kwargs.get('query'))}")
async def search_places(query: str, filters: dict):
    """Cached search with custom key builder"""
    return await database.search_places(query, filters)
```

## Frontend Architecture

### HTML Structure
```html
<!DOCTYPE html>
<html lang="sv">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Traditional Swedish Fika - Discover Authentic Fika Locations</title>
    <meta name="description" content="Discover the best traditional Swedish fika locations across Stockholm, Gothenburg, Malmö, Uppsala, and Västerås.">
    
    <!-- SEO optimizations -->
    <meta property="og:title" content="Traditional Swedish Fika Register">
    <meta property="og:description" content="Find authentic fika experiences in Sweden's major cities">
    <meta property="og:type" content="website">
    
    <!-- Schema.org structured data -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Traditional Swedish Fika",
        "url": "https://swedishfika.com",
        "description": "Directory of traditional Swedish fika locations"
    }
    </script>
</head>
```

### CSS Framework (Custom + Responsive)
```css
/* Modern, clean design inspired by Swedish minimalism */
:root {
    --primary-blue: #004B87;      /* Swedish flag blue */
    --accent-yellow: #FECC02;     /* Swedish flag yellow */
    --warm-beige: #F5E6D3;       /* Fika warmth */
    --deep-brown: #8B4513;       /* Coffee brown */
    --clean-white: #FEFEFE;
    --text-dark: #2C2C2C;
}

.fika-card {
    background: var(--clean-white);
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0,75,135,0.1);
    transition: transform 0.2s ease;
}

.city-nav {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
}
```

### JavaScript Features
```javascript
// Progressive enhancement for search
class FikaSearch {
    constructor() {
        this.searchInput = document.getElementById('search');
        this.resultsContainer = document.getElementById('results');
        this.debounceTimer = null;
        this.init();
    }
    
    init() {
        this.searchInput.addEventListener('input', this.handleSearch.bind(this));
    }
    
    handleSearch(event) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.performSearch(event.target.value);
        }, 300);
    }
    
    async performSearch(query) {
        if (query.length < 2) return;
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await response.json();
            this.displayResults(results);
        } catch (error) {
            console.error('Search failed:', error);
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new FikaSearch();
});
```

## Docker Development Environment

### Docker Compose Structure
```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - /app/__pycache__
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/fika_dev
      - REDIS_URL=redis://redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    depends_on:
      - db
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: python -m http.server 3000

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=fika_dev
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
```

### Development Dockerfile (Backend)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## Deployment Strategy

### Digital Ocean Setup
```yaml
# Digital Ocean App Platform Configuration
name: swedish-fika-register
region: fra
services:
- name: backend
  source_dir: /backend
  github:
    repo: your-username/swedish-fika-register
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /ai
  env_vars:
  - key: DATABASE_URL
    scope: RUN_AND_BUILD_TIME
    type: SECRET
  - key: REDIS_URL
    scope: RUN_TIME
    type: SECRET

- name: frontend
  source_dir: /frontend
  github:
    repo: your-username/swedish-fika-register
    branch: main
  run_command: python -m http.server 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /

databases:
- name: fika-db
  engine: PG
  version: "15"
  
static_sites:
- name: assets
  source_dir: /frontend/static
```

### Environment Variables
```bash
# Development
DATABASE_URL=postgresql://postgres:password@localhost:5432/fika_dev
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
OPENROUTER_API_KEY=your-openrouter-key
UPSTASH_REDIS_URL=your-upstash-redis-url
UPSTASH_REDIS_TOKEN=your-upstash-token

# Production
DATABASE_URL=${DATABASE_URL}  # Managed by Digital Ocean
REDIS_URL=${REDIS_URL}        # Upstash Redis URL
ENVIRONMENT=production
LOG_LEVEL=INFO
```

## AI Features Implementation

### LangChain Agents
```python
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from langchain.memory import ConversationBufferMemory

class FikaRecommendationSystem:
    def __init__(self):
        self.llm = OpenAI(
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=settings.OPENROUTER_API_KEY,
            model_name="anthropic/claude-3-haiku"
        )
        
        self.tools = [
            Tool(
                name="Search Places",
                func=self.search_places,
                description="Search for fika places by criteria"
            ),
            Tool(
                name="Get Reviews",
                func=self.get_place_reviews,
                description="Get reviews for a specific place"
            ),
        ]
        
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent="conversational-react-description",
            memory=ConversationBufferMemory(memory_key="chat_history"),
            verbose=True
        )
    
    async def get_recommendations(self, user_preferences: dict) -> list:
        """Generate personalized fika recommendations"""
        prompt = f"""
        Based on these preferences: {user_preferences}
        Recommend 5 traditional Swedish fika places that would be perfect.
        Consider: location, atmosphere, traditional pastries, price range.
        """
        
        response = await self.agent.arun(prompt)
        return self.parse_recommendations(response)
```

### Content Moderation
```python
class ContentModerationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-3.5-turbo")
        
    async def moderate_review(self, review_text: str) -> dict:
        """Moderate user reviews for inappropriate content"""
        prompt = f"""
        Analyze this review for a Swedish fika location and determine:
        1. Is it appropriate? (yes/no)
        2. Toxicity level (0-1)
        3. Contains spam? (yes/no)
        4. Language detected
        
        Review: "{review_text}"
        
        Respond in JSON format.
        """
        
        response = await self.llm.agenerate([prompt])
        return json.loads(response.generations[0][0].text)
```

## Performance Optimizations

### Database Optimizations
- Geographic indexing for location-based queries
- Full-text search indexes for place names and descriptions
- Materialized views for complex aggregations
- Connection pooling with asyncpg

### Caching Strategy
- Redis for API response caching
- CDN for static assets
- Browser caching headers
- Database query result caching

### SEO Optimizations
- Server-side rendering for public pages
- Structured data markup (Schema.org)
- Open Graph tags
- Sitemap generation
- Robots.txt optimization

## Security Considerations

### API Security
- Rate limiting on all endpoints
- Input validation and sanitization
- SQL injection prevention
- CORS configuration
- API key authentication for admin routes

### Data Protection
- Encryption at rest (Supabase)
- TLS/SSL encryption in transit
- Environment variable security
- Secret key rotation
- User data anonymization

## Monitoring and Analytics

### Application Monitoring
```python
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
REQUEST_COUNT = Counter('fika_requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('fika_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

### Usage Analytics
- API endpoint usage tracking
- Geographic distribution of users
- Popular search terms
- Most viewed fika locations
- AI recommendation effectiveness

## Development Workflow

### Local Development Setup
```bash
# Clone repository
git clone https://github.com/your-username/swedish-fika-register.git
cd swedish-fika-register

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start development environment
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head

# Load initial data
docker-compose exec backend python scripts/load_initial_data.py
```

### Database Migrations
```bash
# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback migration
docker-compose exec backend alembic downgrade -1
```

### Testing Strategy
```python
# pytest configuration
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_get_places_by_city(client):
    response = client.get("/api/places?city=Stockholm")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(place["city"] == "Stockholm" for place in data)
```

## Initial Data Population

### Seed Data Structure
The application will be populated with curated data for:
- 50+ traditional fika locations per major city
- Historical konditoris and modern fika spots
- Traditional Swedish pastries and specialties
- User reviews and ratings (anonymized sample data)
- Categories and tags for filtering

### Data Sources
- Tourism boards (Visit Stockholm, Gothenburg & Co, etc.)
- Cultural heritage sites
- Local fika enthusiast communities
- Traditional konditori associations
- Food and travel blogs

This implementation provides a solid foundation for a scalable, AI-powered Swedish fika discovery platform with modern web technologies and best practices.