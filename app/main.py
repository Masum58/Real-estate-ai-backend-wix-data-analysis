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

# 🔥 CORS CONFIGURATION FOR WIX
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dev-sitex-1858428749.wix-development-sites.org",
        "https://*.wixsite.com",
        "https://*.wix.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Origin",
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers"
    ],
    expose_headers=["*"],
    max_age=600
)

@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "Real Estate AI Valuation API is running"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

app.include_router(
    valuation_router,
    prefix="/api",
    tags=["Valuation"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )