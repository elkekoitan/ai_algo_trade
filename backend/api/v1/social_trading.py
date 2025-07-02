"""
Social Trading API Endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.modules.social_trading import (
    SocialTradingService, UserProfile, SocialPost, TradingSignal,
    Community, Leaderboard, PostType, SignalType
)

router = APIRouter(prefix="/social", tags=["social-trading"])

# Initialize service
social_service = SocialTradingService()

@router.on_event("startup")
async def startup_social_service():
    """Start social trading service"""
    await social_service.start_service()

# User Profile Endpoints
@router.post("/profile", response_model=UserProfile)
async def create_user_profile(profile_data: Dict[str, Any]):
    """Create or update user profile"""
    try:
        return await social_service.create_user_profile(profile_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/profile/{user_id}", response_model=Optional[UserProfile])
async def get_user_profile(user_id: str):
    """Get user profile"""
    profile = await social_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    return profile

@router.put("/profile/{user_id}/metrics")
async def update_user_metrics(user_id: str, metrics: Dict[str, Any]):
    """Update user trading metrics"""
    success = await social_service.update_user_metrics(user_id, metrics)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}

# Social Posts Endpoints
@router.post("/posts", response_model=SocialPost)
async def create_post(post_data: Dict[str, Any]):
    """Create a social trading post"""
    try:
        return await social_service.create_post(post_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/feed/{user_id}")
async def get_social_feed(
    user_id: str,
    limit: int = 20,
    post_type: Optional[PostType] = None
):
    """Get personalized social feed"""
    feed = await social_service.get_feed(user_id, limit, post_type)
    return {"posts": feed, "count": len(feed)}

@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, user_id: str):
    """Like a social post"""
    success = await social_service.like_post(user_id, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"success": True}

# Trading Signals Endpoints
@router.post("/signals", response_model=TradingSignal)
async def create_signal(signal_data: Dict[str, Any]):
    """Create a trading signal"""
    try:
        return await social_service.create_signal(signal_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/signals")
async def get_active_signals(
    user_id: Optional[str] = None,
    symbol: Optional[str] = None,
    limit: int = 50
):
    """Get active trading signals"""
    signals = await social_service.get_active_signals(user_id, symbol, limit)
    return {"signals": signals, "count": len(signals)}

# Follow System Endpoints
@router.post("/follow")
async def follow_user(follower_id: str, following_id: str):
    """Follow another user"""
    success = await social_service.follow_user(follower_id, following_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot follow user")
    return {"success": True}

@router.delete("/follow")
async def unfollow_user(follower_id: str, following_id: str):
    """Unfollow a user"""
    success = await social_service.unfollow_user(follower_id, following_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot unfollow user")
    return {"success": True}

# Leaderboard Endpoints
@router.get("/leaderboard")
async def get_leaderboard(period: str = "monthly", limit: int = 100):
    """Get trading leaderboard"""
    leaderboard = await social_service.get_leaderboard(period, limit)
    return {"leaderboard": leaderboard, "count": len(leaderboard)}

# Community Endpoints
@router.post("/communities", response_model=Community)
async def create_community(community_data: Dict[str, Any]):
    """Create a trading community"""
    try:
        return await social_service.create_community(community_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/communities/trending")
async def get_trending_communities(limit: int = 10):
    """Get trending communities"""
    communities = await social_service.get_trending_communities(limit)
    return {"communities": communities, "count": len(communities)}

# Analytics Endpoints
@router.get("/analytics/user/{user_id}")
async def get_user_analytics(user_id: str):
    """Get user social analytics"""
    profile = await social_service.get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "profile": profile,
        "engagement": {
            "posts_count": profile.posts_count,
            "likes_received": profile.likes_received,
            "followers_count": profile.followers_count,
            "reputation_score": profile.reputation_score
        },
        "trading_performance": {
            "total_return": profile.total_return,
            "monthly_return": profile.monthly_return,
            "win_rate": profile.win_rate,
            "total_trades": profile.total_trades
        }
    }

@router.get("/analytics/trending")
async def get_trending_topics():
    """Get trending trading topics"""
    # Mock implementation - would analyze hashtags and mentions
    return {
        "trending_topics": [
            {"topic": "#bitcoin", "mentions": 156, "sentiment": "bullish"},
            {"topic": "#forex", "mentions": 89, "sentiment": "neutral"},
            {"topic": "#ethereum", "mentions": 67, "sentiment": "bullish"},
            {"topic": "#gold", "mentions": 45, "sentiment": "bearish"},
            {"topic": "#sp500", "mentions": 34, "sentiment": "neutral"}
        ],
        "trending_symbols": [
            {"symbol": "BTCUSD", "mentions": 89, "sentiment": "bullish"},
            {"symbol": "EURUSD", "mentions": 67, "sentiment": "neutral"},
            {"symbol": "XAUUSD", "mentions": 45, "sentiment": "bearish"},
            {"symbol": "GBPUSD", "mentions": 34, "sentiment": "neutral"},
            {"symbol": "ETHUSD", "mentions": 23, "sentiment": "bullish"}
        ]
    } 