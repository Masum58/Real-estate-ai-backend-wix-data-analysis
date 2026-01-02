import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.run_valuation import router as valuation_router

# --------------------------------------------------
# Load environment variables
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
# 🔥 CORS CONFIG (FIXED FOR WIX)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.wix-development-sites\.org|https://.*\.wixsite\.com|https://www\.wix\.com",
    allow_credentials=True,
    allow_methods=["*"],     # POST, OPTIONS, GET
    allow_headers=["*"],     # Content-Type, Authorization
)

# --------------------------------------------------
# Root endpoint
# --------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Real Estate AI Valuation API is running"
    }

# --------------------------------------------------
# Health check endpoint
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
