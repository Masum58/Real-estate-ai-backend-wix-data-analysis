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

# 🔥 CORS – ALLOW ALL (FIXES WIX ISSUE)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 👈 IMPORTANT
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
