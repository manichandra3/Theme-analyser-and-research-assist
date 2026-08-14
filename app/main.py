from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os
from datetime import datetime
import json

from .routers import documents, search, qa, evaluation
from .core.config import settings
from .db.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Document Processing API",
    description="API for document processing with OCR capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(qa.router, prefix="/api/v1", tags=["qa"])
app.include_router(evaluation.router, prefix="/api/v1", tags=["evaluation"])

@app.get("/")
async def root():
    return {"message": "Document Processing API is running"} 