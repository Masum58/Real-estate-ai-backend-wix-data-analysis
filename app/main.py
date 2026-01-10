import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.run_valuation import router as valuation_router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Real Estate AI Valuation API",
    version="2.0.0",  # Updated to reflect 1-mile radius + weight system
    description=(
        "AI-powered real estate valuation API using MLS data. "
        "Features 1-mile radius comparable selection with distance-based weighting."
    )
)

# 🔥 CRITICAL: CORS MUST BE CONFIGURED BEFORE ROUTES
# Allows Wix frontend to communicate with this API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (suitable for public API)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Specific methods we use
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600  # Cache preflight for 1 hour
)

@app.get("/")
def root():
    """
    Root endpoint - API status check
    """
    return {
        "status": "online",
        "service": "Real Estate AI Valuation API",
        "version": "2.0.0",
        "features": [
            "1-mile radius comparable selection",
            "Distance-based property weighting",
            "NC/SC cross-state support",
            "AI-powered market analysis"
        ],
        "cors": "enabled",
        "endpoints": {
            "health": "/health",
            "valuation": "/api/run-valuation",
            "docs": "/docs"
        }
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring services (UptimeRobot, etc.)
    """
    return {
        "status": "healthy",
        "cors": "enabled",
        "api_version": "2.0.0"
    }

# Include valuation router AFTER CORS middleware
app.include_router(
    valuation_router,
    prefix="/api",
    tags=["Valuation"]
)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Disable reload in production
    )