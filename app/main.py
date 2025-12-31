import os
from dotenv import load_dotenv
from fastapi import FastAPI

from app.api.run_valuation import router as valuation_router

# --------------------------------------------------
# Load environment variables from .env
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Create FastAPI app
# --------------------------------------------------
app = FastAPI(
    title="Real Estate AI Valuation API",
    version="1.0.0",
    description="Backend API for AI-powered real estate valuation using MLS data"
)

# --------------------------------------------------
# Root endpoint (for browser / client confidence)
# --------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Real Estate AI Valuation API is running"
    }

# --------------------------------------------------
# Health check endpoint (for monitoring)
# --------------------------------------------------
@app.get("/health")
def health_check():
    return {"status": "healthy"}

# --------------------------------------------------
# Register API routes
# --------------------------------------------------
app.include_router(
    valuation_router,
    prefix="/api",
    tags=["Valuation"]
)

# --------------------------------------------------
# Local development entry point
# --------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
