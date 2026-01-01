#!/usr/bin/env python3
"""
Quick start script for PriceHunt
"""
import uvicorn

if __name__ == "__main__":
    print("🔍 Starting PriceHunt - Price Comparison Agent")
    print("=" * 50)
    print("Open http://localhost:8000 in your browser")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

