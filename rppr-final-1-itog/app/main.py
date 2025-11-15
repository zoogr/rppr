from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .database import create_tables, engine
from .models import Base
from .api import app as api_router

# Загрузка переменных окружения
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Student Management API...")
    create_tables()
    print("✅ Database tables created")
    yield
    # Shutdown
    print("👋 Shutting down Student Management API...")

app = FastAPI(
    title="Student Management API",
    description="Full-featured Student Management System with Auth, Caching, and Background Tasks",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Подключение роутеров
app.include_router(api_router)

@app.get("/")
async def root():
    return {
        "message": "Student Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if os.getenv("DEBUG", "False").lower() == "true" else False
    )