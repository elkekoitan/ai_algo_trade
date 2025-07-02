"""
Social Trading Data Models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

class UserTier(str, Enum):
    ROOKIE = "rookie"
    TRADER = "trader"
    PRO = "pro"
    EXPERT = "expert"
    LEGEND = "legend"

class PostType(str, Enum):
    ANALYSIS = "analysis"
    SIGNAL = "signal"
    EDUCATION = "education"
    DISCUSSION = "discussion"
    CELEBRATION = "celebration"
    WARNING = "warning"

class SignalType(str, Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE = "close"

class CommunityType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    PREMIUM = "premium"

class UserProfile(BaseModel):
    """Enhanced user profile for social trading"""
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    
    # Trading credentials
    tier: UserTier = UserTier.ROOKIE
    verified: bool = False
    trading_since: Optional[datetime] = None
    
    # Performance metrics
    total_return: float = 0.0
    monthly_return: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0
    followers_count: int = 0
    following_count: int = 0
    
    # Social metrics
    posts_count: int = 0
    likes_received: int = 0
    comments_count: int = 0
    reputation_score: float = 0.0
    
    # Achievements
    badges: List[str] = []
    achievements: List[Dict[str, Any]] = []
    
    # Settings
    is_public: bool = True
    allow_copy_trading: bool = False
    premium_member: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

class SocialPost(BaseModel):
    """Social media style trading post"""
    post_id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    
    # Content
    post_type: PostType
    title: Optional[str] = None
    content: str
    images: List[str] = []
    charts: List[Dict[str, Any]] = []
    
    # Trading related
    symbols_mentioned: List[str] = []
    signal: Optional[Dict[str, Any]] = None
    trade_idea: Optional[Dict[str, Any]] = None
    
    # Engagement
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    views_count: int = 0
    
    # Metadata
    tags: List[str] = []
    is_pinned: bool = False
    is_featured: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class TradingSignal(BaseModel):
    """Social trading signal"""
    signal_id: str
    user_id: str
    username: str
    
    # Signal details
    signal_type: SignalType
    symbol: str
    entry_price: Optional[float] = None
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    confidence: float = Field(ge=0, le=100)
    
    # Analysis
    reasoning: str
    timeframe: str = "H1"
    risk_reward_ratio: Optional[float] = None
    
    # Social metrics
    followers_count: int = 0
    likes_count: int = 0
    comments_count: int = 0
    
    # Performance tracking
    is_active: bool = True
    current_pnl: float = 0.0
    max_profit: float = 0.0
    max_loss: float = 0.0
    
    # Metadata
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

class Community(BaseModel):
    """Trading community/group"""
    community_id: str
    name: str
    description: str
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    
    # Settings
    community_type: CommunityType = CommunityType.PUBLIC
    invite_only: bool = False
    moderated: bool = True
    
    # Stats
    members_count: int = 0
    posts_count: int = 0
    active_members: int = 0
    
    # Management
    creator_id: str
    moderators: List[str] = []
    rules: List[str] = []
    tags: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Leaderboard(BaseModel):
    """Trading leaderboard entry"""
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    tier: UserTier
    
    # Performance metrics
    rank: int
    total_return: float
    monthly_return: float
    weekly_return: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    sharpe_ratio: float
    
    # Social metrics
    followers_count: int
    signals_accuracy: float
    reputation_score: float
    
    # Period
    period: str = "monthly"  # daily, weekly, monthly, yearly, all-time
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class SocialTrade(BaseModel):
    """Social trade with sharing capabilities"""
    trade_id: str
    user_id: str
    
    # Trade details
    symbol: str
    trade_type: str
    volume: float
    entry_price: float
    exit_price: Optional[float] = None
    profit_loss: Optional[float] = None
    
    # Social sharing
    is_shared: bool = False
    post_id: Optional[str] = None
    celebration_message: Optional[str] = None
    
    # Analytics
    views_count: int = 0
    likes_count: int = 0
    copy_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    closed_at: Optional[datetime] = None

class FollowRelation(BaseModel):
    """Follow relationship between users"""
    follower_id: str
    following_id: str
    
    # Settings
    notifications_enabled: bool = True
    copy_trading_enabled: bool = False
    signal_alerts: bool = True
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SocialComment(BaseModel):
    """Comment on social posts"""
    comment_id: str
    post_id: str
    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    
    content: str
    parent_comment_id: Optional[str] = None  # For replies
    
    likes_count: int = 0
    replies_count: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SocialNotification(BaseModel):
    """Social trading notification"""
    notification_id: str
    user_id: str
    
    # Notification details
    type: str  # follow, like, comment, signal, trade_update
    title: str
    message: str
    
    # Related objects
    related_user_id: Optional[str] = None
    related_post_id: Optional[str] = None
    related_signal_id: Optional[str] = None
    
    # Status
    is_read: bool = False
    is_important: bool = False
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TradingChallenge(BaseModel):
    """Social trading challenge/competition"""
    challenge_id: str
    title: str
    description: str
    
    # Challenge settings
    start_date: datetime
    end_date: datetime
    entry_fee: float = 0.0
    prize_pool: float = 0.0
    max_participants: int = 100
    
    # Rules
    starting_balance: float = 10000.0
    allowed_instruments: List[str] = []
    max_position_size: float = 0.1
    
    # Stats
    participants_count: int = 0
    current_leader: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow) 