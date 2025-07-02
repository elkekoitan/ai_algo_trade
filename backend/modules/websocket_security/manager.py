import asyncio
import json
import time
import hashlib
from typing import Dict, Set, Optional, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from fastapi import WebSocket, WebSocketDisconnect
import redis
import logging
from cryptography.fernet import Fernet
import jwt

logger = logging.getLogger(__name__)

@dataclass
class WebSocketConnection:
    websocket: WebSocket
    user_id: str
    connection_id: str
    ip_address: str
    user_agent: str
    connected_at: datetime
    last_activity: datetime
    subscription_topics: Set[str]
    rate_limit_tokens: int
    is_authenticated: bool

@dataclass
class WebSocketMessage:
    connection_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: datetime
    encrypted: bool = False

class WebSocketSecurityManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.active_connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.rate_limits = {
            'messages_per_minute': 60,
            'subscriptions_per_connection': 10,
            'max_connections_per_user': 5,
            'max_message_size': 1024  # bytes
        }
        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        
    async def authenticate_connection(self, websocket: WebSocket, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate WebSocket connection using JWT token"""
        try:
            # Verify JWT token
            payload = jwt.decode(token, options={"verify_signature": False})  # In production, verify signature
            user_id = payload.get('sub')
            
            if not user_id:
                return None
                
            # Check if user exists and is active
            user_data = await self._get_user_data(user_id)
            if not user_data or not user_data.get('is_active', False):
                return None
                
            return {
                'user_id': user_id,
                'email': user_data.get('email'),
                'role': user_data.get('role', 'user')
            }
            
        except Exception as e:
            logger.error(f"WebSocket authentication failed: {e}")
            return None
    
    async def register_connection(self, websocket: WebSocket, user_id: str, 
                                ip_address: str, user_agent: str) -> str:
        """Register a new WebSocket connection"""
        # Generate unique connection ID
        connection_id = self._generate_connection_id(user_id, ip_address)
        
        # Check connection limits
        if not await self._check_connection_limits(user_id, ip_address):
            raise Exception("Connection limit exceeded")
        
        # Create connection object
        connection = WebSocketConnection(
            websocket=websocket,
            user_id=user_id,
            connection_id=connection_id,
            ip_address=ip_address,
            user_agent=user_agent,
            connected_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            subscription_topics=set(),
            rate_limit_tokens=self.rate_limits['messages_per_minute'],
            is_authenticated=True
        )
        
        # Store connection
        self.active_connections[connection_id] = connection
        
        # Update user connections mapping
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Store in Redis for persistence
        await self._store_connection_info(connection)
        
        # Update connection count metrics
        await self._update_connection_metrics()
        
        logger.info(f"WebSocket connection registered: {connection_id} for user {user_id}")
        return connection_id
    
    async def unregister_connection(self, connection_id: str):
        """Unregister a WebSocket connection"""
        if connection_id not in self.active_connections:
            return
            
        connection = self.active_connections[connection_id]
        user_id = connection.user_id
        
        # Remove from active connections
        del self.active_connections[connection_id]
        
        # Update user connections mapping
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from Redis
        await self._remove_connection_info(connection_id)
        
        # Update connection count metrics
        await self._update_connection_metrics()
        
        logger.info(f"WebSocket connection unregistered: {connection_id}")
    
    async def handle_message(self, connection_id: str, message: str) -> bool:
        """Handle incoming WebSocket message with security checks"""
        if connection_id not in self.active_connections:
            return False
            
        connection = self.active_connections[connection_id]
        
        # Rate limiting check
        if not await self._check_rate_limit(connection):
            logger.warning(f"Rate limit exceeded for connection {connection_id}")
            await self._send_error(connection.websocket, "RATE_LIMIT_EXCEEDED", 
                                 "Too many messages. Please slow down.")
            return False
        
        # Message size check
        if len(message.encode('utf-8')) > self.rate_limits['max_message_size']:
            logger.warning(f"Message too large from connection {connection_id}")
            await self._send_error(connection.websocket, "MESSAGE_TOO_LARGE", 
                                 "Message exceeds maximum size limit.")
            return False
        
        # Parse and validate message
        try:
            parsed_message = json.loads(message)
            if not self._validate_message_structure(parsed_message):
                await self._send_error(connection.websocket, "INVALID_MESSAGE_FORMAT", 
                                     "Invalid message format.")
                return False
        except json.JSONDecodeError:
            await self._send_error(connection.websocket, "INVALID_JSON", 
                                 "Invalid JSON format.")
            return False
        
        # Update last activity
        connection.last_activity = datetime.utcnow()
        
        # Process message based on type
        await self._process_message(connection, parsed_message)
        
        return True
    
    async def subscribe_to_topic(self, connection_id: str, topic: str) -> bool:
        """Subscribe connection to a topic"""
        if connection_id not in self.active_connections:
            return False
            
        connection = self.active_connections[connection_id]
        
        # Check subscription limits
        if len(connection.subscription_topics) >= self.rate_limits['subscriptions_per_connection']:
            await self._send_error(connection.websocket, "SUBSCRIPTION_LIMIT_EXCEEDED", 
                                 "Maximum number of subscriptions reached.")
            return False
        
        # Validate topic access permissions
        if not await self._check_topic_permissions(connection.user_id, topic):
            await self._send_error(connection.websocket, "PERMISSION_DENIED", 
                                 "Access denied for this topic.")
            return False
        
        # Add subscription
        connection.subscription_topics.add(topic)
        
        # Store subscription in Redis
        await self.redis.sadd(f"ws_subscriptions:{connection_id}", topic)
        await self.redis.sadd(f"topic_subscribers:{topic}", connection_id)
        
        logger.info(f"Connection {connection_id} subscribed to topic: {topic}")
        return True
    
    async def unsubscribe_from_topic(self, connection_id: str, topic: str) -> bool:
        """Unsubscribe connection from a topic"""
        if connection_id not in self.active_connections:
            return False
            
        connection = self.active_connections[connection_id]
        connection.subscription_topics.discard(topic)
        
        # Remove subscription from Redis
        await self.redis.srem(f"ws_subscriptions:{connection_id}", topic)
        await self.redis.srem(f"topic_subscribers:{topic}", connection_id)
        
        logger.info(f"Connection {connection_id} unsubscribed from topic: {topic}")
        return True
    
    async def broadcast_to_topic(self, topic: str, message: Dict[str, Any], 
                               encrypt: bool = False):
        """Broadcast message to all subscribers of a topic"""
        # Get topic subscribers from Redis
        subscribers = await self.redis.smembers(f"topic_subscribers:{topic}")
        
        if not subscribers:
            return
        
        # Prepare message
        broadcast_message = {
            'type': 'broadcast',
            'topic': topic,
            'payload': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Encrypt if requested
        if encrypt:
            broadcast_message = await self._encrypt_message(broadcast_message)
        
        message_str = json.dumps(broadcast_message)
        
        # Send to all active subscribers
        for subscriber_bytes in subscribers:
            connection_id = subscriber_bytes.decode()
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                try:
                    await connection.websocket.send_text(message_str)
                except Exception as e:
                    logger.error(f"Failed to send message to {connection_id}: {e}")
                    # Remove broken connection
                    await self.unregister_connection(connection_id)
    
    async def send_to_user(self, user_id: str, message: Dict[str, Any], 
                          encrypt: bool = False):
        """Send message to all connections of a specific user"""
        if user_id not in self.user_connections:
            return
        
        # Prepare message
        user_message = {
            'type': 'direct',
            'payload': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Encrypt if requested
        if encrypt:
            user_message = await self._encrypt_message(user_message)
        
        message_str = json.dumps(user_message)
        
        # Send to all user connections
        for connection_id in self.user_connections[user_id].copy():
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                try:
                    await connection.websocket.send_text(message_str)
                except Exception as e:
                    logger.error(f"Failed to send message to {connection_id}: {e}")
                    await self.unregister_connection(connection_id)
    
    def _generate_connection_id(self, user_id: str, ip_address: str) -> str:
        """Generate unique connection ID"""
        timestamp = str(int(time.time() * 1000))
        data = f"{user_id}:{ip_address}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    async def _check_connection_limits(self, user_id: str, ip_address: str) -> bool:
        """Check if connection limits are respected"""
        # Check per-user connection limit
        user_connection_count = len(self.user_connections.get(user_id, set()))
        if user_connection_count >= self.rate_limits['max_connections_per_user']:
            return False
        
        # Check per-IP connection limit (simple implementation)
        ip_connections = sum(1 for conn in self.active_connections.values() 
                           if conn.ip_address == ip_address)
        if ip_connections >= 10:  # Max 10 connections per IP
            return False
        
        return True
    
    async def _check_rate_limit(self, connection: WebSocketConnection) -> bool:
        """Check rate limiting for connection"""
        current_time = datetime.utcnow()
        
        # Simple token bucket implementation
        if connection.rate_limit_tokens > 0:
            connection.rate_limit_tokens -= 1
            return True
        
        # Check if we should refill tokens (every minute)
        time_diff = (current_time - connection.last_activity).total_seconds()
        if time_diff >= 60:  # 1 minute
            connection.rate_limit_tokens = self.rate_limits['messages_per_minute']
            return True
        
        return False
    
    def _validate_message_structure(self, message: Dict[str, Any]) -> bool:
        """Validate message structure"""
        required_fields = ['type', 'payload']
        return all(field in message for field in required_fields)
    
    async def _process_message(self, connection: WebSocketConnection, message: Dict[str, Any]):
        """Process incoming message based on type"""
        message_type = message.get('type')
        payload = message.get('payload', {})
        
        if message_type == 'subscribe':
            topic = payload.get('topic')
            if topic:
                await self.subscribe_to_topic(connection.connection_id, topic)
        
        elif message_type == 'unsubscribe':
            topic = payload.get('topic')
            if topic:
                await self.unsubscribe_from_topic(connection.connection_id, topic)
        
        elif message_type == 'ping':
            await self._send_pong(connection.websocket)
        
        elif message_type == 'trading_action':
            # Handle trading-related messages
            await self._handle_trading_message(connection, payload)
        
        else:
            await self._send_error(connection.websocket, "UNKNOWN_MESSAGE_TYPE", 
                                 f"Unknown message type: {message_type}")
    
    async def _handle_trading_message(self, connection: WebSocketConnection, payload: Dict[str, Any]):
        """Handle trading-related WebSocket messages"""
        # This would integrate with your trading modules
        # For now, just log the message
        logger.info(f"Trading message from {connection.connection_id}: {payload}")
    
    async def _check_topic_permissions(self, user_id: str, topic: str) -> bool:
        """Check if user has permission to access topic"""
        # Get user role
        user_data = await self._get_user_data(user_id)
        user_role = user_data.get('role', 'user')
        
        # Define topic permissions
        topic_permissions = {
            'market_data': ['user', 'premium', 'admin'],
            'trading_signals': ['premium', 'admin'],
            'admin_alerts': ['admin'],
            'user_notifications': ['user', 'premium', 'admin']
        }
        
        allowed_roles = topic_permissions.get(topic, [])
        return user_role in allowed_roles
    
    async def _encrypt_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt message payload"""
        try:
            message_str = json.dumps(message)
            encrypted_data = self.fernet.encrypt(message_str.encode())
            return {
                'encrypted': True,
                'data': encrypted_data.decode()
            }
        except Exception as e:
            logger.error(f"Failed to encrypt message: {e}")
            return message
    
    async def _send_error(self, websocket: WebSocket, error_code: str, error_message: str):
        """Send error message to WebSocket"""
        error_response = {
            'type': 'error',
            'error_code': error_code,
            'message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        }
        try:
            await websocket.send_text(json.dumps(error_response))
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")
    
    async def _send_pong(self, websocket: WebSocket):
        """Send pong response"""
        pong_response = {
            'type': 'pong',
            'timestamp': datetime.utcnow().isoformat()
        }
        try:
            await websocket.send_text(json.dumps(pong_response))
        except Exception as e:
            logger.error(f"Failed to send pong: {e}")
    
    async def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data from cache or database"""
        # Try Redis cache first
        cached_data = await self.redis.get(f"user_data:{user_id}")
        if cached_data:
            return json.loads(cached_data.decode())
        
        # If not in cache, would fetch from database
        # For now, return mock data
        return {
            'user_id': user_id,
            'email': f"user{user_id}@example.com",
            'role': 'user',
            'is_active': True
        }
    
    async def _store_connection_info(self, connection: WebSocketConnection):
        """Store connection info in Redis"""
        connection_data = {
            'user_id': connection.user_id,
            'connection_id': connection.connection_id,
            'ip_address': connection.ip_address,
            'user_agent': connection.user_agent,
            'connected_at': connection.connected_at.isoformat(),
            'is_authenticated': connection.is_authenticated
        }
        
        await self.redis.setex(
            f"ws_connection:{connection.connection_id}",
            3600,  # 1 hour TTL
            json.dumps(connection_data)
        )
    
    async def _remove_connection_info(self, connection_id: str):
        """Remove connection info from Redis"""
        await self.redis.delete(f"ws_connection:{connection_id}")
        await self.redis.delete(f"ws_subscriptions:{connection_id}")
    
    async def _update_connection_metrics(self):
        """Update connection count metrics"""
        total_connections = len(self.active_connections)
        await self.redis.set("websocket_connections", total_connections)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            'total_connections': len(self.active_connections),
            'unique_users': len(self.user_connections),
            'connections_by_user': {
                user_id: len(connections) 
                for user_id, connections in self.user_connections.items()
            },
            'recent_activity': [
                {
                    'connection_id': conn.connection_id,
                    'user_id': conn.user_id,
                    'last_activity': conn.last_activity.isoformat(),
                    'subscriptions': len(conn.subscription_topics)
                }
                for conn in list(self.active_connections.values())[-10:]  # Last 10 connections
            ]
        }

# Global WebSocket security manager instance
websocket_security_manager = None

async def get_websocket_security_manager() -> WebSocketSecurityManager:
    """Get global WebSocket security manager instance"""
    global websocket_security_manager
    if websocket_security_manager is None:
        import redis.asyncio as redis
        redis_client = redis.Redis(host='localhost', port=6379, db=3)
        websocket_security_manager = WebSocketSecurityManager(redis_client)
    return websocket_security_manager 