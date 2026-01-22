from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api import router

# Create FastAPI app
app = FastAPI(
    title="Agent Simulation Platform API",
    description="API for multi-turn agent interactions and evaluations",
    version="1.0.0"
)

# CORS middleware for frontend communication
# Allow localhost for development and production frontend URL
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

# Add production frontend URL if specified
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

# Allow Vercel preview deployments (*.vercel.app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["simulations"])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Agent Simulation Platform API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "anthropic_api_key": "set" if os.getenv("ANTHROPIC_API_KEY") else "missing",
        "openai_api_key": "set" if os.getenv("OPENAI_API_KEY") else "missing",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
