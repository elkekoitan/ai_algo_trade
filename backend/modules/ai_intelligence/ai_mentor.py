"""
Advanced AI Mentor System
Personalized trading coach with adaptive learning and behavioral analysis
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
import numpy as np
from enum import Enum

from .advanced_ai_service import AdvancedAIService
from ..mt5_integration.service import MT5Service
from ...core.enhanced_event_bus import enhanced_event_bus

logger = logging.getLogger(__name__)

class MentorPersonality(str, Enum):
    SUPPORTIVE = "supportive"
    ANALYTICAL = "analytical"
    MOTIVATIONAL = "motivational"
    STRICT = "strict"
    FRIENDLY = "friendly"

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"

class TradingLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class MentorSession:
    """AI Mentor coaching session"""
    
    def __init__(self):
        self.session_id = f"session_{datetime.utcnow().isoformat()}"
        self.start_time = datetime.utcnow()
        self.messages: List[Dict[str, Any]] = []
        self.insights_given = 0
        self.corrections_made = 0
        self.encouragements_given = 0
        self.user_mood = "neutral"
        self.session_goals: List[str] = []

class UserProfile:
    """Enhanced user profile for AI mentoring"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.trading_level = TradingLevel.BEGINNER
        self.learning_style = LearningStyle.VISUAL
        self.preferred_personality = MentorPersonality.SUPPORTIVE
        
        # Trading psychology
        self.risk_tolerance = 0.5  # 0-1 scale
        self.emotional_state = "neutral"
        self.confidence_level = 0.5
        self.discipline_score = 0.5
        
        # Learning progress
        self.concepts_mastered: List[str] = []
        self.weak_areas: List[str] = []
        self.learning_goals: List[str] = []
        self.progress_milestones: List[Dict[str, Any]] = []
        
        # Trading patterns
        self.common_mistakes: List[str] = []
        self.successful_patterns: List[str] = []
        self.preferred_timeframes: List[str] = []
        self.favorite_instruments: List[str] = []
        
        # Session history
        self.total_sessions = 0
        self.total_session_time = 0
        self.last_session = None
        self.mentor_feedback_score = 0.0

class AIMentorService:
    """Advanced AI Mentor Service"""
    
    def __init__(self):
        self.ai_service = AdvancedAIService()
        self.mt5_service = MT5Service()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.active_sessions: Dict[str, MentorSession] = {}
        self.is_running = False
        
        # Mentor knowledge base
        self.trading_concepts = self._load_trading_concepts()
        self.coaching_strategies = self._load_coaching_strategies()
        self.psychological_frameworks = self._load_psychological_frameworks()
        
    async def start_service(self):
        """Start AI mentor service"""
        self.is_running = True
        logger.info("🧠 AI Mentor Service started")
        
        # Start background analysis
        asyncio.create_task(self._analyze_user_behavior())
        asyncio.create_task(self._update_learning_paths())
        asyncio.create_task(self._monitor_emotional_states())
        
    # Core Mentoring Functions
    async def start_mentoring_session(
        self, 
        user_id: str,
        session_goals: Optional[List[str]] = None
    ) -> MentorSession:
        """Start a personalized mentoring session"""
        try:
            # Get or create user profile
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserProfile(user_id)
                
            profile = self.user_profiles[user_id]
            
            # Create new session
            session = MentorSession()
            session.session_goals = session_goals or []
            self.active_sessions[user_id] = session
            
            # Analyze current user state
            user_state = await self._analyze_current_state(user_id)
            
            # Generate personalized welcome message
            welcome_message = await self._generate_welcome_message(profile, user_state)
            
            session.messages.append({
                "type": "mentor",
                "content": welcome_message,
                "timestamp": datetime.utcnow(),
                "mood": "welcoming"
            })
            
            # Update profile
            profile.total_sessions += 1
            profile.last_session = datetime.utcnow()
            
            logger.info(f"🎯 Mentoring session started for {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Failed to start mentoring session: {e}")
            raise
            
    async def process_user_message(
        self, 
        user_id: str, 
        message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process user message and provide mentoring response"""
        try:
            if user_id not in self.active_sessions:
                await self.start_mentoring_session(user_id)
                
            session = self.active_sessions[user_id]
            profile = self.user_profiles[user_id]
            
            # Add user message to session
            session.messages.append({
                "type": "user",
                "content": message,
                "timestamp": datetime.utcnow(),
                "context": context or {}
            })
            
            # Analyze message sentiment and intent
            analysis = await self._analyze_message(message, profile)
            
            # Generate personalized response
            response = await self._generate_mentor_response(
                message, profile, session, analysis, context
            )
            
            # Add mentor response to session
            session.messages.append({
                "type": "mentor",
                "content": response["content"],
                "timestamp": datetime.utcnow(),
                "analysis": analysis,
                "suggestions": response.get("suggestions", []),
                "resources": response.get("resources", [])
            })
            
            # Update user profile based on interaction
            await self._update_profile_from_interaction(profile, message, analysis)
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process user message: {e}")
            return {
                "content": "I apologize, but I'm having trouble processing your message right now. Let me try to help you in a different way.",
                "type": "error"
            }
            
    async def provide_trade_analysis(
        self, 
        user_id: str, 
        trade_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Provide detailed trade analysis and coaching"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                profile = UserProfile(user_id)
                self.user_profiles[user_id] = profile
                
            # Analyze the trade
            analysis = await self._analyze_trade_decision(trade_data, profile)
            
            # Generate coaching feedback
            feedback = await self._generate_trade_feedback(analysis, profile)
            
            # Update user's trading patterns
            await self._update_trading_patterns(profile, trade_data, analysis)
            
            return {
                "analysis": analysis,
                "feedback": feedback,
                "recommendations": analysis.get("recommendations", []),
                "learning_points": analysis.get("learning_points", []),
                "risk_assessment": analysis.get("risk_assessment", {}),
                "psychological_insights": analysis.get("psychological_insights", {})
            }
            
        except Exception as e:
            logger.error(f"Failed to provide trade analysis: {e}")
            return {"error": "Analysis unavailable"}
            
    async def create_personalized_learning_path(
        self, 
        user_id: str
    ) -> Dict[str, Any]:
        """Create personalized learning path"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                return {"error": "User profile not found"}
                
            # Assess current knowledge level
            knowledge_assessment = await self._assess_knowledge_level(profile)
            
            # Identify learning gaps
            learning_gaps = await self._identify_learning_gaps(profile, knowledge_assessment)
            
            # Create structured learning path
            learning_path = await self._create_learning_path(profile, learning_gaps)
            
            # Generate practice exercises
            exercises = await self._generate_practice_exercises(profile, learning_path)
            
            return {
                "learning_path": learning_path,
                "current_level": knowledge_assessment,
                "learning_gaps": learning_gaps,
                "recommended_exercises": exercises,
                "estimated_completion_time": self._estimate_completion_time(learning_path),
                "milestones": self._create_milestones(learning_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to create learning path: {e}")
            return {"error": "Learning path creation failed"}
            
    async def provide_psychological_coaching(
        self, 
        user_id: str,
        emotional_state: str,
        trading_situation: Optional[str] = None
    ) -> Dict[str, Any]:
        """Provide psychological coaching and emotional support"""
        try:
            profile = self.user_profiles.get(user_id)
            if not profile:
                profile = UserProfile(user_id)
                self.user_profiles[user_id] = profile
                
            # Update emotional state
            profile.emotional_state = emotional_state
            
            # Analyze psychological state
            psychological_analysis = await self._analyze_psychological_state(
                profile, emotional_state, trading_situation
            )
            
            # Generate coaching response
            coaching_response = await self._generate_psychological_coaching(
                profile, psychological_analysis
            )
            
            # Provide coping strategies
            coping_strategies = await self._suggest_coping_strategies(
                emotional_state, trading_situation
            )
            
            # Update confidence and discipline scores
            await self._update_psychological_metrics(profile, emotional_state)
            
            return {
                "coaching_message": coaching_response,
                "psychological_insights": psychological_analysis,
                "coping_strategies": coping_strategies,
                "recommended_actions": psychological_analysis.get("recommended_actions", []),
                "mindfulness_exercises": self._get_mindfulness_exercises(emotional_state),
                "confidence_level": profile.confidence_level,
                "discipline_score": profile.discipline_score
            }
            
        except Exception as e:
            logger.error(f"Failed to provide psychological coaching: {e}")
            return {"error": "Psychological coaching unavailable"}
            
    # Analysis Methods
    async def _analyze_current_state(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's current trading and emotional state"""
        try:
            # Get recent trading data
            recent_trades = await self._get_recent_trades(user_id)
            
            # Get current market positions
            positions = []
            if self.mt5_service.is_connected():
                positions = await self.mt5_service.get_positions()
                
            # Analyze performance
            performance = await self._analyze_recent_performance(recent_trades)
            
            # Assess emotional indicators
            emotional_indicators = await self._assess_emotional_indicators(
                recent_trades, positions
            )
            
            return {
                "recent_performance": performance,
                "current_positions": len(positions),
                "emotional_indicators": emotional_indicators,
                "trading_frequency": len(recent_trades),
                "risk_exposure": self._calculate_risk_exposure(positions),
                "last_activity": datetime.utcnow() - timedelta(hours=1)  # Mock
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze current state: {e}")
            return {}
            
    async def _analyze_message(
        self, 
        message: str, 
        profile: UserProfile
    ) -> Dict[str, Any]:
        """Analyze user message for sentiment, intent, and learning needs"""
        try:
            # Use AI service for sentiment analysis
            sentiment_analysis = await self.ai_service.analyze_sentiment(message)
            
            # Detect trading-related intent
            intent_analysis = await self._detect_intent(message)
            
            # Identify learning opportunities
            learning_opportunities = await self._identify_learning_opportunities(
                message, profile
            )
            
            # Assess emotional state from message
            emotional_assessment = await self._assess_emotional_state_from_text(message)
            
            return {
                "sentiment": sentiment_analysis,
                "intent": intent_analysis,
                "learning_opportunities": learning_opportunities,
                "emotional_state": emotional_assessment,
                "complexity_level": self._assess_message_complexity(message),
                "topics_mentioned": self._extract_trading_topics(message)
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze message: {e}")
            return {}
            
    async def _generate_mentor_response(
        self,
        message: str,
        profile: UserProfile,
        session: MentorSession,
        analysis: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate personalized mentor response"""
        try:
            # Build context for AI
            ai_context = self._build_ai_context(profile, session, analysis, context)
            
            # Generate response based on personality and learning style
            base_response = await self._generate_base_response(
                message, ai_context, profile.preferred_personality
            )
            
            # Add learning elements
            learning_elements = await self._add_learning_elements(
                base_response, profile, analysis
            )
            
            # Include motivational elements
            motivational_elements = await self._add_motivational_elements(
                base_response, profile, session
            )
            
            # Suggest next actions
            next_actions = await self._suggest_next_actions(
                message, profile, analysis
            )
            
            # Provide resources
            resources = await self._suggest_resources(
                analysis.get("topics_mentioned", []), profile
            )
            
            return {
                "content": base_response + learning_elements + motivational_elements,
                "suggestions": next_actions,
                "resources": resources,
                "learning_focus": analysis.get("learning_opportunities", []),
                "emotional_support": self._get_emotional_support_level(analysis),
                "complexity_adjustment": self._adjust_for_complexity(profile)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate mentor response: {e}")
            return {
                "content": "I understand you're looking for guidance. Let me help you step by step.",
                "suggestions": ["Ask me about a specific trading concept", "Share your current trading challenge"],
                "resources": []
            }
            
    # Helper Methods
    def _load_trading_concepts(self) -> Dict[str, Any]:
        """Load trading concepts database"""
        return {
            "risk_management": {
                "level": "fundamental",
                "description": "Managing trading risk through position sizing and stop losses",
                "subtopics": ["position_sizing", "stop_loss", "risk_reward_ratio", "diversification"]
            },
            "technical_analysis": {
                "level": "intermediate", 
                "description": "Analyzing price charts and patterns",
                "subtopics": ["support_resistance", "trend_analysis", "indicators", "chart_patterns"]
            },
            "fundamental_analysis": {
                "level": "intermediate",
                "description": "Analyzing economic factors affecting markets",
                "subtopics": ["economic_indicators", "news_analysis", "earnings", "central_banks"]
            },
            "trading_psychology": {
                "level": "advanced",
                "description": "Managing emotions and mindset in trading",
                "subtopics": ["fear_greed", "discipline", "patience", "confidence"]
            },
            "strategy_development": {
                "level": "advanced",
                "description": "Creating and testing trading strategies",
                "subtopics": ["backtesting", "optimization", "forward_testing", "strategy_evaluation"]
            }
        }
        
    def _load_coaching_strategies(self) -> Dict[str, Any]:
        """Load coaching strategies for different situations"""
        return {
            "losing_streak": {
                "approach": "supportive_analytical",
                "focus": ["risk_management", "emotional_control", "strategy_review"],
                "tone": "understanding_but_constructive"
            },
            "overconfidence": {
                "approach": "cautionary_educational",
                "focus": ["risk_awareness", "humility", "continuous_learning"],
                "tone": "respectful_but_firm"
            },
            "fear_paralysis": {
                "approach": "encouraging_gradual",
                "focus": ["confidence_building", "small_steps", "positive_reinforcement"],
                "tone": "warm_supportive"
            },
            "analysis_paralysis": {
                "approach": "action_oriented",
                "focus": ["decision_making", "simplification", "time_management"],
                "tone": "direct_helpful"
            }
        }
        
    def _load_psychological_frameworks(self) -> Dict[str, Any]:
        """Load psychological frameworks for coaching"""
        return {
            "cognitive_behavioral": {
                "description": "Identify and change negative thought patterns",
                "techniques": ["thought_challenging", "behavioral_experiments", "mindfulness"]
            },
            "positive_psychology": {
                "description": "Focus on strengths and positive emotions",
                "techniques": ["strength_identification", "gratitude_practice", "flow_state"]
            },
            "growth_mindset": {
                "description": "Embrace challenges as learning opportunities",
                "techniques": ["reframing_failures", "process_focus", "continuous_improvement"]
            }
        }
        
    async def _generate_welcome_message(
        self, 
        profile: UserProfile, 
        user_state: Dict[str, Any]
    ) -> str:
        """Generate personalized welcome message"""
        try:
            # Customize based on personality preference
            if profile.preferred_personality == MentorPersonality.MOTIVATIONAL:
                base = "Welcome back, champion! 🚀 Ready to crush your trading goals today?"
            elif profile.preferred_personality == MentorPersonality.ANALYTICAL:
                base = "Hello! Let's dive into some analytical insights for your trading journey."
            elif profile.preferred_personality == MentorPersonality.SUPPORTIVE:
                base = "Hi there! I'm here to support you every step of the way. 😊"
            elif profile.preferred_personality == MentorPersonality.STRICT:
                base = "Welcome. Let's focus on disciplined trading and proper risk management."
            else:  # FRIENDLY
                base = "Hey! Great to see you again! What's on your trading mind today? 😄"
                
            # Add state-specific context
            if user_state.get("recent_performance", {}).get("profitable", False):
                base += " I see you've been doing well lately - let's keep that momentum going!"
            elif user_state.get("recent_performance", {}).get("losses", 0) > 0:
                base += " I noticed some recent challenges. Let's work together to turn things around."
                
            # Add session goals if any
            if hasattr(profile, 'learning_goals') and profile.learning_goals:
                base += f" I remember you wanted to work on {', '.join(profile.learning_goals[:2])}."
                
            return base
            
        except Exception as e:
            logger.error(f"Failed to generate welcome message: {e}")
            return "Welcome! I'm your AI trading mentor, ready to help you improve your trading skills."
            
    async def _analyze_trade_decision(
        self, 
        trade_data: Dict[str, Any], 
        profile: UserProfile
    ) -> Dict[str, Any]:
        """Analyze a trade decision for coaching purposes"""
        try:
            analysis = {
                "risk_assessment": {},
                "technical_analysis": {},
                "psychological_factors": {},
                "recommendations": [],
                "learning_points": []
            }
            
            # Risk assessment
            position_size = trade_data.get("volume", 0)
            account_balance = trade_data.get("account_balance", 10000)
            risk_percent = (position_size * trade_data.get("pip_value", 1)) / account_balance * 100
            
            analysis["risk_assessment"] = {
                "position_size": position_size,
                "risk_percentage": risk_percent,
                "appropriate_risk": risk_percent <= profile.risk_tolerance * 100,
                "risk_level": "high" if risk_percent > 5 else "medium" if risk_percent > 2 else "low"
            }
            
            # Technical analysis
            if "entry_reason" in trade_data:
                analysis["technical_analysis"] = {
                    "entry_reason": trade_data["entry_reason"],
                    "has_stop_loss": "stop_loss" in trade_data,
                    "has_take_profit": "take_profit" in trade_data,
                    "risk_reward_ratio": self._calculate_risk_reward(trade_data)
                }
                
            # Psychological factors
            analysis["psychological_factors"] = {
                "emotional_state": profile.emotional_state,
                "confidence_level": profile.confidence_level,
                "potential_biases": self._identify_potential_biases(trade_data, profile)
            }
            
            # Generate recommendations
            analysis["recommendations"] = await self._generate_trade_recommendations(
                analysis, profile
            )
            
            # Learning points
            analysis["learning_points"] = await self._extract_learning_points(
                analysis, profile
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze trade decision: {e}")
            return {}
            
    # Background Tasks
    async def _analyze_user_behavior(self):
        """Background task to analyze user behavior patterns"""
        while self.is_running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                for user_id, profile in self.user_profiles.items():
                    # Analyze trading patterns
                    await self._update_trading_patterns_analysis(profile)
                    
                    # Update learning progress
                    await self._update_learning_progress(profile)
                    
                    # Assess psychological state
                    await self._assess_psychological_trends(profile)
                    
                logger.info("🔍 User behavior analysis completed")
                
            except Exception as e:
                logger.error(f"User behavior analysis error: {e}")
                await asyncio.sleep(60)
                
    async def _update_learning_paths(self):
        """Background task to update personalized learning paths"""
        while self.is_running:
            try:
                await asyncio.sleep(1800)  # Every 30 minutes
                
                for user_id, profile in self.user_profiles.items():
                    # Update learning path based on progress
                    await self._adapt_learning_path(profile)
                    
                    # Suggest new learning materials
                    await self._suggest_new_materials(profile)
                    
                logger.info("📚 Learning paths updated")
                
            except Exception as e:
                logger.error(f"Learning path update error: {e}")
                await asyncio.sleep(60)
                
    async def _monitor_emotional_states(self):
        """Background task to monitor emotional states"""
        while self.is_running:
            try:
                await asyncio.sleep(600)  # Every 10 minutes
                
                for user_id, profile in self.user_profiles.items():
                    # Monitor for emotional distress
                    if profile.emotional_state in ["stressed", "frustrated", "fearful"]:
                        await self._provide_emotional_support(user_id, profile)
                        
                    # Check for overconfidence
                    if profile.confidence_level > 0.9:
                        await self._provide_humility_reminder(user_id, profile)
                        
                logger.info("💭 Emotional states monitored")
                
            except Exception as e:
                logger.error(f"Emotional monitoring error: {e}")
                await asyncio.sleep(60)
                
    # Utility Methods
    def _calculate_risk_reward(self, trade_data: Dict[str, Any]) -> float:
        """Calculate risk-reward ratio"""
        try:
            entry = trade_data.get("entry_price", 0)
            stop_loss = trade_data.get("stop_loss", 0)
            take_profit = trade_data.get("take_profit", 0)
            
            if not all([entry, stop_loss, take_profit]):
                return 0.0
                
            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            
            return reward / risk if risk > 0 else 0.0
            
        except Exception:
            return 0.0
            
    def _identify_potential_biases(
        self, 
        trade_data: Dict[str, Any], 
        profile: UserProfile
    ) -> List[str]:
        """Identify potential cognitive biases"""
        biases = []
        
        # Overconfidence bias
        if profile.confidence_level > 0.8:
            biases.append("overconfidence")
            
        # Loss aversion
        if trade_data.get("stop_loss") and not trade_data.get("take_profit"):
            biases.append("loss_aversion")
            
        # Confirmation bias
        if len(profile.successful_patterns) > len(profile.common_mistakes) * 2:
            biases.append("confirmation_bias")
            
        return biases
        
    async def _get_recent_trades(self, user_id: str) -> List[Dict[str, Any]]:
        """Get recent trades for analysis"""
        # Mock implementation - would connect to actual trade history
        return [
            {
                "symbol": "EURUSD",
                "type": "buy",
                "volume": 0.1,
                "profit": 25.0,
                "timestamp": datetime.utcnow() - timedelta(hours=2)
            },
            {
                "symbol": "GBPUSD", 
                "type": "sell",
                "volume": 0.2,
                "profit": -15.0,
                "timestamp": datetime.utcnow() - timedelta(hours=6)
            }
        ] 