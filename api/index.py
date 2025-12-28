#!/usr/bin/env python3
"""
Vercel Serverless Entry Point
This file adapts FastAPI for Vercel's serverless environment
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment for serverless
os.environ.setdefault("VERCEL", "1")

# Import ASGI handler for Vercel
from mangum import Mangum
from main import app

# Create handler for Vercel
handler = Mangum(app, lifespan="off")

# Vercel expects a handler function
def lambda_handler(event, context):
    """AWS Lambda handler for Vercel"""
    return handler(event, context)

# For local testing with Vercel CLI
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
