from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import redis.asyncio as redis
from contextlib import asynccontextmanager
import logging
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from .config import settings, get_redis_url
from .database import connect_to_database, disconnect_from_database, check_database_health
from .api import places, reviews, ai

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Metrics
REQUEST_COUNT = Counter('fika_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('fika_request_duration_seconds', 'Request duration', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Swedish Fika Register API")
    
    # Connect to database
    await connect_to_database()
    
    # Setup Redis cache
    redis_client = redis.from_url(
        get_redis_url(), 
        encoding="utf-8", 
        decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis_client), prefix="fika-cache")
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await disconnect_from_database()
    await redis_client.close()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="API for discovering traditional Swedish fika locations",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url] if not settings.debug else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    
    return response

# Include routers
app.include_router(places.router, prefix="/api/places", tags=["places"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])

# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

@app.get("/health/detailed", tags=["health"])
async def detailed_health_check():
    """Detailed health check with database connectivity"""
    db_healthy = await check_database_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": "connected" if db_healthy else "disconnected",
        "timestamp": time.time()
    }

# Metrics endpoint
@app.get("/metrics", tags=["monitoring"])
async def get_metrics():
    """Prometheus metrics endpoint"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Root endpoint - redirect to frontend
@app.get("/", response_class=RedirectResponse, tags=["root"])
async def root():
    """Redirect to frontend application"""
    return RedirectResponse(url=settings.frontend_url)

# Frontend city pages (for SEO)
@app.get("/stockholm", response_class=HTMLResponse, tags=["frontend"])
async def stockholm_page():
    """Stockholm fika locations page"""
    # This will be replaced with actual HTML template rendering
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traditional Swedish Fika in Stockholm</title>
        <meta name="description" content="Discover the best traditional fika locations in Stockholm, Sweden's capital city.">
    </head>
    <body>
        <h1>Traditional Swedish Fika in Stockholm</h1>
        <p>Coming soon - Stockholm's best fika locations!</p>
    </body>
    </html>
    """)

@app.get("/gothenburg", response_class=HTMLResponse, tags=["frontend"])
async def gothenburg_page():
    """Gothenburg fika locations page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traditional Swedish Fika in Gothenburg</title>
        <meta name="description" content="Discover the best traditional fika locations in Gothenburg.">
    </head>
    <body>
        <h1>Traditional Swedish Fika in Gothenburg</h1>
        <p>Coming soon - Gothenburg's best fika locations including Café Husaren!</p>
    </body>
    </html>
    """)

@app.get("/malmo", response_class=HTMLResponse, tags=["frontend"])
async def malmo_page():
    """Malmö fika locations page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traditional Swedish Fika in Malmö</title>
        <meta name="description" content="Discover the best traditional fika locations in Malmö.">
    </head>
    <body>
        <h1>Traditional Swedish Fika in Malmö</h1>
        <p>Coming soon - Malmö's best fika locations!</p>
    </body>
    </html>
    """)

@app.get("/uppsala", response_class=HTMLResponse, tags=["frontend"])
async def uppsala_page():
    """Uppsala fika locations page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traditional Swedish Fika in Uppsala</title>
        <meta name="description" content="Discover the best traditional fika locations in Uppsala.">
    </head>
    <body>
        <h1>Traditional Swedish Fika in Uppsala</h1>
        <p>Coming soon - Uppsala's best fika locations!</p>
    </body>
    </html>
    """)

@app.get("/vasteras", response_class=HTMLResponse, tags=["frontend"])
async def vasteras_page():
    """Västerås fika locations page"""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Traditional Swedish Fika in Västerås</title>
        <meta name="description" content="Discover the best traditional fika locations in Västerås.">
    </head>
    <body>
        <h1>Traditional Swedish Fika in Västerås</h1>
        <p>Coming soon - Västerås's best fika locations!</p>
    </body>
    </html>
    """)

# Custom exception handler
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {exc}")
    return {
        "status_code": 500,
        "message": "Internal server error",
        "detail": str(exc) if settings.debug else "An error occurred"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )