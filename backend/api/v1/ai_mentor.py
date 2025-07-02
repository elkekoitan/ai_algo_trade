"""
AI Mentor API Endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.modules.ai_intelligence.ai_mentor import AIMentorService

router = APIRouter(prefix="/ai-mentor", tags=["ai-mentor"])

# Initialize service
mentor_service = AIMentorService()

@router.on_event("startup")
async def startup_mentor_service():
    """Start AI mentor service"""
    await mentor_service.start_service()

# Mentoring Session Endpoints
@router.post("/session/start")
async def start_mentoring_session(
    user_id: str,
    session_goals: Optional[List[str]] = None
):
    """Start a personalized mentoring session"""
    try:
        session = await mentor_service.start_mentoring_session(user_id, session_goals)
        return {
            "session_id": session.session_id,
            "start_time": session.start_time,
            "goals": session.session_goals,
            "welcome_message": session.messages[-1]["content"] if session.messages else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/message")
async def process_user_message(
    user_id: str,
    message: str,
    context: Optional[Dict[str, Any]] = None
):
    """Process user message and get mentor response"""
    try:
        response = await mentor_service.process_user_message(user_id, message, context)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Trade Analysis Endpoints
@router.post("/analyze/trade")
async def analyze_trade(user_id: str, trade_data: Dict[str, Any]):
    """Provide detailed trade analysis and coaching"""
    try:
        analysis = await mentor_service.provide_trade_analysis(user_id, trade_data)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Learning Path Endpoints
@router.get("/learning-path/{user_id}")
async def get_learning_path(user_id: str):
    """Get personalized learning path"""
    try:
        learning_path = await mentor_service.create_personalized_learning_path(user_id)
        return learning_path
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Psychological Coaching Endpoints
@router.post("/coaching/psychological")
async def get_psychological_coaching(
    user_id: str,
    emotional_state: str,
    trading_situation: Optional[str] = None
):
    """Get psychological coaching and emotional support"""
    try:
        coaching = await mentor_service.provide_psychological_coaching(
            user_id, emotional_state, trading_situation
        )
        return coaching
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# User Profile Endpoints
@router.get("/profile/{user_id}")
async def get_mentor_profile(user_id: str):
    """Get user's mentoring profile"""
    profile = mentor_service.user_profiles.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    return {
        "user_id": profile.user_id,
        "trading_level": profile.trading_level,
        "learning_style": profile.learning_style,
        "preferred_personality": profile.preferred_personality,
        "confidence_level": profile.confidence_level,
        "discipline_score": profile.discipline_score,
        "concepts_mastered": profile.concepts_mastered,
        "weak_areas": profile.weak_areas,
        "learning_goals": profile.learning_goals,
        "total_sessions": profile.total_sessions,
        "total_session_time": profile.total_session_time,
        "mentor_feedback_score": profile.mentor_feedback_score
    }

@router.put("/profile/{user_id}")
async def update_mentor_profile(user_id: str, profile_data: Dict[str, Any]):
    """Update user's mentoring profile"""
    if user_id not in mentor_service.user_profiles:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    profile = mentor_service.user_profiles[user_id]
    
    # Update allowed fields
    allowed_fields = [
        "trading_level", "learning_style", "preferred_personality",
        "learning_goals", "risk_tolerance"
    ]
    
    for field, value in profile_data.items():
        if field in allowed_fields and hasattr(profile, field):
            setattr(profile, field, value)
    
    return {"success": True}

# Analytics Endpoints
@router.get("/analytics/{user_id}")
async def get_mentor_analytics(user_id: str):
    """Get mentoring analytics for user"""
    profile = mentor_service.user_profiles.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    session = mentor_service.active_sessions.get(user_id)
    
    return {
        "learning_progress": {
            "concepts_mastered": len(profile.concepts_mastered),
            "weak_areas": len(profile.weak_areas),
            "progress_milestones": profile.progress_milestones,
            "current_level": profile.trading_level
        },
        "session_stats": {
            "total_sessions": profile.total_sessions,
            "total_time": profile.total_session_time,
            "current_session_active": session is not None,
            "current_session_duration": (
                (datetime.utcnow() - session.start_time).total_seconds() / 60
                if session else 0
            )
        },
        "psychological_metrics": {
            "confidence_level": profile.confidence_level,
            "discipline_score": profile.discipline_score,
            "emotional_state": profile.emotional_state,
            "risk_tolerance": profile.risk_tolerance
        },
        "trading_patterns": {
            "common_mistakes": profile.common_mistakes,
            "successful_patterns": profile.successful_patterns,
            "preferred_timeframes": profile.preferred_timeframes,
            "favorite_instruments": profile.favorite_instruments
        }
    }

# Knowledge Base Endpoints
@router.get("/knowledge/concepts")
async def get_trading_concepts():
    """Get available trading concepts"""
    return mentor_service.trading_concepts

@router.get("/knowledge/coaching-strategies")
async def get_coaching_strategies():
    """Get coaching strategies"""
    return mentor_service.coaching_strategies

@router.get("/knowledge/psychological-frameworks")
async def get_psychological_frameworks():
    """Get psychological frameworks"""
    return mentor_service.psychological_frameworks

# Quick Help Endpoints
@router.post("/quick-help")
async def get_quick_help(
    user_id: str,
    topic: str,
    urgency: str = "normal"  # low, normal, high, critical
):
    """Get quick help on a specific topic"""
    try:
        # Generate quick help response
        help_content = {
            "risk_management": "Remember the golden rule: Never risk more than 1-2% of your account on a single trade. Use stop losses and position sizing to protect your capital.",
            "emotional_control": "Take a deep breath. Emotions are the enemy of good trading. Step away from the charts for a moment and reassess your strategy objectively.",
            "strategy_review": "Let's review your recent trades. Look for patterns in your wins and losses. What worked? What didn't? Adjust accordingly.",
            "market_analysis": "Focus on the bigger picture. What's the overall trend? Are you trading with or against it? Use multiple timeframes for confirmation."
        }
        
        quick_response = help_content.get(
            topic, 
            "I'm here to help! Can you be more specific about what you need assistance with?"
        )
        
        # Add urgency-based modifications
        if urgency == "critical":
            quick_response = "🚨 " + quick_response + " If you're in a losing position, consider cutting your losses now."
        elif urgency == "high":
            quick_response = "⚠️ " + quick_response + " Take immediate action to protect your capital."
        
        return {
            "topic": topic,
            "urgency": urgency,
            "quick_help": quick_response,
            "follow_up_actions": [
                "Start a full mentoring session for detailed guidance",
                "Review your trading plan",
                "Check your risk management rules",
                "Take a break if feeling emotional"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/motivational-quote")
async def get_motivational_quote():
    """Get a motivational trading quote"""
    quotes = [
        "The market is a device for transferring money from the impatient to the patient. - Warren Buffett",
        "Risk comes from not knowing what you're doing. - Warren Buffett",
        "The stock market is filled with individuals who know the price of everything, but the value of nothing. - Philip Fisher",
        "It's not whether you're right or wrong that's important, but how much money you make when you're right and how much you lose when you're wrong. - George Soros",
        "The way to make money is to buy when blood is running in the streets. - John D. Rockefeller",
        "Discipline is the bridge between goals and accomplishment. - Jim Rohn",
        "The most important quality for an investor is temperament, not intellect. - Warren Buffett",
        "Trading is not about being right or wrong. It's about how much you make when you're right and how much you lose when you're wrong. - Anonymous"
    ]
    
    import random
    quote = random.choice(quotes)
    
    return {
        "quote": quote,
        "timestamp": datetime.utcnow(),
        "category": "motivation"
    } 