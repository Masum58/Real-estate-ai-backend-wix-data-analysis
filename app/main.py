import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
# 🔥 CORS CONFIG (REQUIRED FOR WIX)
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dev-sitex-1858428749.wix-development-sites.org",
        "https://www.wix.com",
        "https://*.wixsite.com",
        "https://*.wix-development-sites.org",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # POST, OPTIONS, etc.
    allow_headers=["*"],   # Content-Type, Authorization, etc.
)

# --------------------------------------------------
# Root endpoint (browser confidence check)
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
