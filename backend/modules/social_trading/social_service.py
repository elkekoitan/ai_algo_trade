"""
Social Trading Service
Advanced social trading platform with community features and social signals
"""
import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from .models import (
    UserProfile, SocialPost, TradingSignal, Community, 
    Leaderboard, SocialTrade, FollowRelation, SocialComment,
    SocialNotification, TradingChallenge, PostType, SignalType
)
from ..mt5_integration.service import MT5Service
from ...core.enhanced_event_bus import enhanced_event_bus

logger = logging.getLogger(__name__)

class SocialTradingService:
    """Advanced social trading service"""
    
    def __init__(self):
        self.mt5_service = MT5Service()
        self.user_profiles: Dict[str, UserProfile] = {}
        self.posts: Dict[str, SocialPost] = {}
        self.signals: Dict[str, TradingSignal] = {}
        self.communities: Dict[str, Community] = {}
        self.follow_relations: Dict[str, List[str]] = {}
        self.is_running = False
        
    async def start_service(self):
        """Start social trading service"""
        self.is_running = True
        logger.info("🚀 Social Trading Service started")
        
        # Initialize with demo data
        await self._initialize_demo_data()
        
        # Start background tasks
        asyncio.create_task(self._update_leaderboards())
        asyncio.create_task(self._process_social_signals())
        asyncio.create_task(self._update_user_metrics())
        
    # User Management
    async def create_user_profile(self, user_data: Dict[str, Any]) -> UserProfile:
        """Create or update user profile"""
        try:
            profile = UserProfile(**user_data)
            self.user_profiles[profile.user_id] = profile
            
            # Broadcast profile creation
            await enhanced_event_bus.publish(
                "social:profile_created",
                {"user_id": profile.user_id, "profile": profile.dict()}
            )
            
            logger.info(f"✅ User profile created: {profile.username}")
            return profile
            
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            raise
            
    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile"""
        return self.user_profiles.get(user_id)
        
    async def update_user_metrics(self, user_id: str, metrics: Dict[str, Any]) -> bool:
        """Update user trading metrics"""
        try:
            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                
                # Update metrics
                for key, value in metrics.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
                
                profile.last_active = datetime.utcnow()
                
                # Update tier based on performance
                await self._update_user_tier(profile)
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to update user metrics: {e}")
            return False
            
    # Social Posts
    async def create_post(self, post_data: Dict[str, Any]) -> SocialPost:
        """Create a social trading post"""
        try:
            post = SocialPost(**post_data)
            self.posts[post.post_id] = post
            
            # Update user stats
            if post.user_id in self.user_profiles:
                self.user_profiles[post.user_id].posts_count += 1
            
            # Broadcast new post
            await enhanced_event_bus.publish(
                "social:post_created",
                {"post": post.dict()}
            )
            
            # Process mentions and tags
            await self._process_post_mentions(post)
            
            logger.info(f"✅ Social post created: {post.post_id}")
            return post
            
        except Exception as e:
            logger.error(f"Failed to create post: {e}")
            raise
            
    async def get_feed(
        self, 
        user_id: str, 
        limit: int = 20,
        post_type: Optional[PostType] = None
    ) -> List[SocialPost]:
        """Get personalized social feed"""
        try:
            # Get user's following list
            following = self.follow_relations.get(user_id, [])
            
            # Get posts from followed users + featured posts
            feed_posts = []
            for post in self.posts.values():
                if (post.user_id in following or 
                    post.is_featured or 
                    post.user_id == user_id):
                    
                    if post_type is None or post.post_type == post_type:
                        feed_posts.append(post)
            
            # Sort by engagement and recency
            feed_posts.sort(key=lambda p: (
                p.likes_count + p.comments_count * 2 + p.views_count * 0.1,
                p.created_at
            ), reverse=True)
            
            return feed_posts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get feed: {e}")
            return []
            
    async def like_post(self, user_id: str, post_id: str) -> bool:
        """Like a social post"""
        try:
            if post_id in self.posts:
                post = self.posts[post_id]
                post.likes_count += 1
                
                # Update post author's reputation
                if post.user_id in self.user_profiles:
                    self.user_profiles[post.user_id].likes_received += 1
                    self.user_profiles[post.user_id].reputation_score += 0.1
                
                # Send notification
                await self._send_notification(
                    post.user_id,
                    "like",
                    f"{user_id} liked your post",
                    f"Your post received a like!",
                    related_user_id=user_id,
                    related_post_id=post_id
                )
                
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to like post: {e}")
            return False
            
    # Trading Signals
    async def create_signal(self, signal_data: Dict[str, Any]) -> TradingSignal:
        """Create a trading signal"""
        try:
            signal = TradingSignal(**signal_data)
            self.signals[signal.signal_id] = signal
            
            # Get current market price for validation
            if self.mt5_service.is_connected():
                try:
                    tick = await self.mt5_service.get_symbol_tick(signal.symbol)
                    current_price = tick.get("ask", 0)
                    
                    # Validate signal against current market
                    if signal.entry_price and abs(signal.entry_price - current_price) / current_price > 0.05:
                        logger.warning(f"Signal price deviation > 5% for {signal.symbol}")
                        
                except Exception as e:
                    logger.warning(f"Could not validate signal price: {e}")
            
            # Broadcast signal
            await enhanced_event_bus.publish(
                "social:signal_created",
                {"signal": signal.dict()}
            )
            
            # Notify followers
            await self._notify_signal_followers(signal)
            
            logger.info(f"✅ Trading signal created: {signal.symbol} {signal.signal_type}")
            return signal
            
        except Exception as e:
            logger.error(f"Failed to create signal: {e}")
            raise
            
    async def get_active_signals(
        self, 
        user_id: Optional[str] = None,
        symbol: Optional[str] = None,
        limit: int = 50
    ) -> List[TradingSignal]:
        """Get active trading signals"""
        try:
            active_signals = [
                signal for signal in self.signals.values()
                if signal.is_active and (
                    user_id is None or signal.user_id == user_id
                ) and (
                    symbol is None or signal.symbol == symbol
                )
            ]
            
            # Sort by confidence and recency
            active_signals.sort(key=lambda s: (s.confidence, s.created_at), reverse=True)
            
            return active_signals[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get active signals: {e}")
            return []
            
    # Follow System
    async def follow_user(self, follower_id: str, following_id: str) -> bool:
        """Follow another user"""
        try:
            if follower_id == following_id:
                return False
                
            # Add to follow relations
            if follower_id not in self.follow_relations:
                self.follow_relations[follower_id] = []
                
            if following_id not in self.follow_relations[follower_id]:
                self.follow_relations[follower_id].append(following_id)
                
                # Update counts
                if follower_id in self.user_profiles:
                    self.user_profiles[follower_id].following_count += 1
                if following_id in self.user_profiles:
                    self.user_profiles[following_id].followers_count += 1
                
                # Send notification
                await self._send_notification(
                    following_id,
                    "follow",
                    f"{follower_id} started following you",
                    f"You have a new follower!",
                    related_user_id=follower_id
                )
                
                logger.info(f"✅ {follower_id} now following {following_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to follow user: {e}")
            return False
            
    async def unfollow_user(self, follower_id: str, following_id: str) -> bool:
        """Unfollow a user"""
        try:
            if (follower_id in self.follow_relations and 
                following_id in self.follow_relations[follower_id]):
                
                self.follow_relations[follower_id].remove(following_id)
                
                # Update counts
                if follower_id in self.user_profiles:
                    self.user_profiles[follower_id].following_count -= 1
                if following_id in self.user_profiles:
                    self.user_profiles[following_id].followers_count -= 1
                
                logger.info(f"✅ {follower_id} unfollowed {following_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Failed to unfollow user: {e}")
            return False
            
    # Leaderboards
    async def get_leaderboard(
        self, 
        period: str = "monthly",
        limit: int = 100
    ) -> List[Leaderboard]:
        """Get trading leaderboard"""
        try:
            leaderboard_entries = []
            
            for rank, (user_id, profile) in enumerate(
                sorted(
                    self.user_profiles.items(),
                    key=lambda x: x[1].total_return,
                    reverse=True
                )[:limit], 1
            ):
                entry = Leaderboard(
                    user_id=user_id,
                    username=profile.username,
                    display_name=profile.display_name,
                    avatar_url=profile.avatar_url,
                    tier=profile.tier,
                    rank=rank,
                    total_return=profile.total_return,
                    monthly_return=profile.monthly_return,
                    weekly_return=profile.monthly_return / 4,  # Approximation
                    win_rate=profile.win_rate,
                    profit_factor=2.5,  # Mock data
                    max_drawdown=15.0,  # Mock data
                    sharpe_ratio=1.8,   # Mock data
                    followers_count=profile.followers_count,
                    signals_accuracy=85.0,  # Mock data
                    reputation_score=profile.reputation_score,
                    period=period
                )
                leaderboard_entries.append(entry)
                
            return leaderboard_entries
            
        except Exception as e:
            logger.error(f"Failed to get leaderboard: {e}")
            return []
            
    # Communities
    async def create_community(self, community_data: Dict[str, Any]) -> Community:
        """Create a trading community"""
        try:
            community = Community(**community_data)
            self.communities[community.community_id] = community
            
            # Broadcast community creation
            await enhanced_event_bus.publish(
                "social:community_created",
                {"community": community.dict()}
            )
            
            logger.info(f"✅ Community created: {community.name}")
            return community
            
        except Exception as e:
            logger.error(f"Failed to create community: {e}")
            raise
            
    async def get_trending_communities(self, limit: int = 10) -> List[Community]:
        """Get trending communities"""
        try:
            communities = list(self.communities.values())
            
            # Sort by activity (members + posts)
            communities.sort(
                key=lambda c: c.members_count + c.posts_count * 2,
                reverse=True
            )
            
            return communities[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get trending communities: {e}")
            return []
            
    # Helper Methods
    async def _initialize_demo_data(self):
        """Initialize with demo social data"""
        try:
            # Create demo users
            demo_users = [
                {
                    "user_id": "user_001",
                    "username": "crypto_king",
                    "display_name": "Crypto King 👑",
                    "bio": "Professional crypto trader with 5+ years experience",
                    "tier": "expert",
                    "verified": True,
                    "total_return": 145.8,
                    "monthly_return": 12.3,
                    "win_rate": 78.5,
                    "followers_count": 1250,
                    "reputation_score": 95.2
                },
                {
                    "user_id": "user_002", 
                    "username": "forex_ninja",
                    "display_name": "Forex Ninja 🥷",
                    "bio": "Scalping specialist, sharing daily setups",
                    "tier": "pro",
                    "verified": True,
                    "total_return": 89.2,
                    "monthly_return": 8.7,
                    "win_rate": 65.4,
                    "followers_count": 890,
                    "reputation_score": 87.1
                },
                {
                    "user_id": "user_003",
                    "username": "swing_master",
                    "display_name": "Swing Master 📈",
                    "bio": "Long-term swing trader, risk management focused",
                    "tier": "pro",
                    "verified": False,
                    "total_return": 67.3,
                    "monthly_return": 5.2,
                    "win_rate": 72.1,
                    "followers_count": 567,
                    "reputation_score": 78.9
                }
            ]
            
            for user_data in demo_users:
                await self.create_user_profile(user_data)
                
            # Create demo posts
            demo_posts = [
                {
                    "post_id": "post_001",
                    "user_id": "user_001",
                    "username": "crypto_king",
                    "display_name": "Crypto King 👑",
                    "post_type": "analysis",
                    "title": "Bitcoin Breaking Key Resistance",
                    "content": "BTC just broke above the 42k resistance level with strong volume. Looking for a continuation to 45k. RSI showing healthy momentum, not overbought yet. This could be the start of the next leg up! 🚀",
                    "symbols_mentioned": ["BTCUSD"],
                    "likes_count": 89,
                    "comments_count": 23,
                    "views_count": 456,
                    "tags": ["bitcoin", "breakout", "bullish"]
                },
                {
                    "post_id": "post_002",
                    "user_id": "user_002",
                    "username": "forex_ninja", 
                    "display_name": "Forex Ninja 🥷",
                    "post_type": "signal",
                    "title": "EURUSD Scalp Setup",
                    "content": "Quick scalp opportunity on EURUSD. Price bouncing off 1.0950 support, looking for a move to 1.0980. Tight stop at 1.0940. Risk:Reward 1:3 ⚡",
                    "symbols_mentioned": ["EURUSD"],
                    "likes_count": 45,
                    "comments_count": 12,
                    "views_count": 234,
                    "tags": ["scalping", "eurusd", "forex"]
                }
            ]
            
            for post_data in demo_posts:
                await self.create_post(post_data)
                
            # Create demo signals
            demo_signals = [
                {
                    "signal_id": "signal_001",
                    "user_id": "user_001", 
                    "username": "crypto_king",
                    "signal_type": "buy",
                    "symbol": "BTCUSD",
                    "entry_price": 42500,
                    "stop_loss": 41000,
                    "take_profit": 45000,
                    "confidence": 85,
                    "reasoning": "Breakout above key resistance with volume confirmation",
                    "timeframe": "H4",
                    "risk_reward_ratio": 1.67,
                    "followers_count": 156,
                    "likes_count": 89
                },
                {
                    "signal_id": "signal_002",
                    "user_id": "user_002",
                    "username": "forex_ninja",
                    "signal_type": "buy",
                    "symbol": "EURUSD",
                    "entry_price": 1.0950,
                    "stop_loss": 1.0940,
                    "take_profit": 1.0980,
                    "confidence": 78,
                    "reasoning": "Support bounce with bullish divergence on RSI",
                    "timeframe": "M15",
                    "risk_reward_ratio": 3.0,
                    "followers_count": 89,
                    "likes_count": 45
                }
            ]
            
            for signal_data in demo_signals:
                await self.create_signal(signal_data)
                
            logger.info("✅ Demo social data initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize demo data: {e}")
            
    async def _update_user_tier(self, profile: UserProfile):
        """Update user tier based on performance"""
        try:
            # Tier calculation based on multiple factors
            score = (
                profile.total_return * 0.3 +
                profile.win_rate * 0.2 +
                profile.reputation_score * 0.2 +
                min(profile.followers_count / 10, 100) * 0.15 +
                min(profile.total_trades / 10, 100) * 0.15
            )
            
            if score >= 90:
                profile.tier = "legend"
            elif score >= 75:
                profile.tier = "expert"
            elif score >= 60:
                profile.tier = "pro"
            elif score >= 40:
                profile.tier = "trader"
            else:
                profile.tier = "rookie"
                
        except Exception as e:
            logger.error(f"Failed to update user tier: {e}")
            
    async def _send_notification(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        **kwargs
    ):
        """Send notification to user"""
        try:
            notification = SocialNotification(
                notification_id=f"notif_{datetime.utcnow().isoformat()}",
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                **kwargs
            )
            
            # Broadcast notification
            await enhanced_event_bus.publish(
                "social:notification",
                {"notification": notification.dict()}
            )
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            
    async def _notify_signal_followers(self, signal: TradingSignal):
        """Notify followers about new signal"""
        try:
            # Get followers of signal creator
            followers = []
            for follower_id, following_list in self.follow_relations.items():
                if signal.user_id in following_list:
                    followers.append(follower_id)
                    
            # Send notifications
            for follower_id in followers:
                await self._send_notification(
                    follower_id,
                    "signal",
                    f"New signal from {signal.username}",
                    f"{signal.signal_type.upper()} {signal.symbol} - {signal.confidence}% confidence",
                    related_user_id=signal.user_id,
                    related_signal_id=signal.signal_id,
                    is_important=True
                )
                
        except Exception as e:
            logger.error(f"Failed to notify signal followers: {e}")
            
    async def _process_post_mentions(self, post: SocialPost):
        """Process mentions and tags in posts"""
        try:
            # Extract @mentions from content
            import re
            mentions = re.findall(r'@(\w+)', post.content)
            
            for mentioned_user in mentions:
                # Find user by username
                for user_id, profile in self.user_profiles.items():
                    if profile.username == mentioned_user:
                        await self._send_notification(
                            user_id,
                            "mention",
                            f"You were mentioned by {post.username}",
                            f"You were mentioned in a post: {post.content[:100]}...",
                            related_user_id=post.user_id,
                            related_post_id=post.post_id
                        )
                        break
                        
        except Exception as e:
            logger.error(f"Failed to process post mentions: {e}")
            
    async def _update_leaderboards(self):
        """Background task to update leaderboards"""
        while self.is_running:
            try:
                # Update leaderboards every hour
                await asyncio.sleep(3600)
                
                # Recalculate user rankings
                await self.get_leaderboard("monthly")
                logger.info("📊 Leaderboards updated")
                
            except Exception as e:
                logger.error(f"Leaderboard update error: {e}")
                await asyncio.sleep(60)
                
    async def _process_social_signals(self):
        """Background task to process social signals"""
        while self.is_running:
            try:
                # Process signals every 30 seconds
                await asyncio.sleep(30)
                
                # Update signal performance
                for signal in self.signals.values():
                    if signal.is_active and self.mt5_service.is_connected():
                        try:
                            tick = await self.mt5_service.get_symbol_tick(signal.symbol)
                            current_price = tick.get("ask", 0)
                            
                            if signal.entry_price and current_price:
                                # Calculate current P&L
                                if signal.signal_type == "buy":
                                    pnl = current_price - signal.entry_price
                                else:
                                    pnl = signal.entry_price - current_price
                                    
                                signal.current_pnl = pnl
                                signal.max_profit = max(signal.max_profit, pnl)
                                signal.max_loss = min(signal.max_loss, pnl)
                                
                        except Exception as e:
                            logger.warning(f"Signal update error for {signal.symbol}: {e}")
                            
            except Exception as e:
                logger.error(f"Signal processing error: {e}")
                await asyncio.sleep(60)
                
    async def _update_user_metrics(self):
        """Background task to update user metrics"""
        while self.is_running:
            try:
                # Update every 5 minutes
                await asyncio.sleep(300)
                
                # Update reputation scores based on recent activity
                for profile in self.user_profiles.values():
                    # Decay reputation over time to encourage activity
                    profile.reputation_score *= 0.999
                    
                logger.info("👥 User metrics updated")
                
            except Exception as e:
                logger.error(f"User metrics update error: {e}")
                await asyncio.sleep(60) 