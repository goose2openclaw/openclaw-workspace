#!/usr/bin/env python3
"""GO2SE 自主系统 v4.0"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

app = FastAPI(title="GO2SE Autonomous v4.0", version="4.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Import routes with error handling
try:
    from routes_v3 import router
    app.include_router(router)
    ROUTES_OK = True
except Exception as e:
    print(f"Routes import error: {e}")
    ROUTES_OK = False
    # Create minimal router
    from fastapi import APIRouter
    router = APIRouter()

@app.get("/health")
def health():
    return {"status": "GO2SE Autonomous v4.0 OK", "version": "4.0", "time": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8025)
