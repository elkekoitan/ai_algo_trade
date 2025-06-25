"""
API module for ICT Ultra v2.
"""

from fastapi import APIRouter
from backend.api.v1 import signals

api_router = APIRouter()
api_router.include_router(signals.router)
