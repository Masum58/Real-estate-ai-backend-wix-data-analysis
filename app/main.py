import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.run_valuation import router as valuation_router

# Load env
load_dotenv()

app = FastAPI(
    title="Real Estate AI Valuation API",
    version="1.0.0",
    description="Backend API for AI-powered real estate valuation using MLS data"
)

# 🔥 CRITICAL: CORS MUST BE CONFIGURED BEFORE ANY ROUTES
# This fixes the "No 'Access-Control-Allow-Origin' header" error

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dev-sitex-1858428749.wix-development-sites.org",
        "https://*.wixsite.com",
        "https://*.wix.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # Allow all origins temporarily for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods including OPTIONS
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600  # Cache preflight for 1 hour
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Real Estate AI Valuation API is running",
        "cors": "enabled"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "cors": "enabled"
    }

# Include router AFTER CORS middleware
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
        reload=False  # Don't use reload in production
    )