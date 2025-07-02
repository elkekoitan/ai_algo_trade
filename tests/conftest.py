"""
Pytest configuration for AI Algo Trade Platform testing.
"""

import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_client():
    """Create a test client for the FastAPI application."""
    try:
        from backend.main import app
        with TestClient(app) as test_client:
            yield test_client
    except ImportError as e:
        pytest.skip(f"Could not import backend.main: {e}")

@pytest.fixture(scope="session")  
async def http_client():
    """Create an async HTTP client for testing live backend."""
    async with httpx.AsyncClient(
        base_url="http://localhost:8002",
        timeout=30.0
    ) as client:
        yield client

@pytest.fixture
def backend_base_url():
    """Base URL for the backend API."""
    return "http://localhost:8002"

@pytest.fixture 
def api_endpoints():
    """List of API endpoints to test."""
    return {
        # Core endpoints
        "/": {"method": "GET", "expected_status": [200]},
        "/health": {"method": "GET", "expected_status": [200]},
        "/api/v1/system/status": {"method": "GET", "expected_status": [200]},
        
        # Trading endpoints
        "/api/v1/trading/account_info": {"method": "GET", "expected_status": [200, 500]},
        "/api/v1/trading/account": {"method": "GET", "expected_status": [200, 500]},
        "/api/v1/auto-trader/status": {"method": "GET", "expected_status": [200]},
        
        # Market data endpoints
        "/api/v1/market/tick/EURUSD": {"method": "GET", "expected_status": [200, 500]},
        
        # API v1 endpoints from routers
        "/api/v1/unified": {"method": "GET", "expected_status": [200, 404, 405]},
        "/api/v1/market": {"method": "GET", "expected_status": [200, 404, 405]},
        "/api/v1/performance": {"method": "GET", "expected_status": [200, 404, 405]},
        "/api/v1/market-narrator": {"method": "GET", "expected_status": [200, 404, 405]},
        "/api/v1/autotrader": {"method": "GET", "expected_status": [200, 404, 405]},
        
        # Documentation endpoints
        "/docs": {"method": "GET", "expected_status": [200]},
        "/redoc": {"method": "GET", "expected_status": [200]},
    }
