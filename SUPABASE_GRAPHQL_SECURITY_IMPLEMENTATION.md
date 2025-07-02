# Supabase Authentication, GraphQL & Enhanced Security Implementation Plan

## Current State Analysis

### 🔍 Current Authentication Status
- **No dedicated auth module exists** in the project structure
- Basic JWT settings present in `backend/core/config/settings.py`:
  - `SECRET_KEY: str = "supersecretkey"`
  - `ALGORITHM: str = "HS256"`
  - `ACCESS_TOKEN_EXPIRE_MINUTES: int = 30`
- No user management, registration, or login endpoints
- All API endpoints are currently **unprotected**
- CORS configured to allow all origins (`allow_origins=["*"]`)

### 🚨 Security Gaps Identified
1. **No authentication middleware**
2. **No authorization checks**
3. **Hard-coded credentials in source code**
4. **Overly permissive CORS settings**
5. **No rate limiting**
6. **No input validation/sanitization**
7. **No API key management**
8. **No session management**

---

## 🎯 Implementation Strategy

### Phase 1: Supabase Authentication Integration

#### 1.1 Supabase Setup & Configuration

```python
# backend/core/config/supabase.py
from supabase import create_client, Client
from typing import Optional
import os

class SupabaseConfig:
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL")
        self.key: str = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
    def get_client(self) -> Client:
        return create_client(self.url, self.key)
    
    def get_admin_client(self) -> Client:
        return create_client(self.url, self.service_role_key)

supabase_config = SupabaseConfig()
```

#### 1.2 Authentication Module Structure

```
backend/modules/auth/
├── __init__.py
├── models.py          # User models and schemas
├── service.py         # Authentication service
├── middleware.py      # Auth middleware
├── dependencies.py    # FastAPI dependencies
├── routes.py          # Auth endpoints
└── utils.py          # JWT and password utilities
```

#### 1.3 User Models & Database Schema

```python
# backend/modules/auth/models.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, JSON
from sqlalchemy.sql import func
from backend.core.database import Base
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)  # Supabase UUID
    email = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String, default="user")  # user, premium, admin
    subscription_plan = Column(String, default="free")
    
    # Trading preferences
    trading_preferences = Column(JSON, default={})
    api_settings = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Trading account settings
    mt5_accounts = Column(JSON, default=[])
    risk_settings = Column(JSON, default={})
    notification_preferences = Column(JSON, default={})
    
    # AI settings
    ai_preferences = Column(JSON, default={})
    strategy_settings = Column(JSON, default={})

# Pydantic schemas
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    role: str
    subscription_plan: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
```

#### 1.4 Authentication Service

```python
# backend/modules/auth/service.py
from supabase import Client
from fastapi import HTTPException, status
from typing import Optional, Dict, Any
import jwt
from datetime import datetime, timedelta
from backend.core.config.settings import get_settings
from backend.core.config.supabase import supabase_config

settings = get_settings()

class AuthService:
    def __init__(self):
        self.supabase: Client = supabase_config.get_client()
        self.admin_supabase: Client = supabase_config.get_admin_client()
    
    async def register_user(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a new user with Supabase Auth"""
        try:
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata or {}
                }
            })
            
            if response.user:
                # Create user profile in our database
                await self.create_user_profile(response.user)
                
            return {
                "user": response.user,
                "session": response.session
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with Supabase"""
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.session:
                # Update last login
                await self.update_last_login(response.user.id)
                
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "user": response.user,
                "expires_in": response.session.expires_in
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            response = self.supabase.auth.refresh_session(refresh_token)
            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_in": response.session.expires_in
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
    
    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token with Supabase"""
        try:
            response = self.supabase.auth.get_user(token)
            return response.user if response.user else None
        except Exception:
            return None
    
    async def logout_user(self, token: str) -> bool:
        """Logout user"""
        try:
            self.supabase.auth.sign_out(token)
            return True
        except Exception:
            return False

auth_service = AuthService()
```

#### 1.5 Authentication Middleware

```python
# backend/modules/auth/middleware.py
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from .service import auth_service

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = await auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user

async def get_current_active_user(current_user = Depends(get_current_user)):
    """Get current active user"""
    if not current_user.get("email_confirmed", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified"
        )
    
    return current_user

def require_role(required_role: str):
    """Decorator to require specific role"""
    def role_checker(current_user = Depends(get_current_active_user)):
        user_role = current_user.get("user_metadata", {}).get("role", "user")
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# Role-specific dependencies
require_admin = require_role("admin")
require_premium = require_role("premium")
```

---

### Phase 2: GraphQL Integration

#### 2.1 GraphQL Setup with Strawberry

```python
# backend/graphql/__init__.py
import strawberry
from typing import List, Optional
from strawberry.fastapi import GraphQLRouter

# Import all GraphQL modules
from .auth import AuthQuery, AuthMutation
from .trading import TradingQuery, TradingMutation
from .ai import AIQuery, AIMutation

@strawberry.type
class Query(AuthQuery, TradingQuery, AIQuery):
    pass

@strawberry.type
class Mutation(AuthMutation, TradingMutation, AIMutation):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
```

#### 2.2 Authentication GraphQL Schema

```python
# backend/graphql/auth.py
import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class User:
    id: str
    email: str
    full_name: Optional[str]
    role: str
    subscription_plan: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

@strawberry.type
class AuthPayload:
    access_token: str
    refresh_token: str
    user: User
    expires_in: int

@strawberry.input
class LoginInput:
    email: str
    password: str

@strawberry.input
class RegisterInput:
    email: str
    password: str
    full_name: Optional[str] = None

@strawberry.type
class AuthQuery:
    @strawberry.field
    async def me(self, info) -> Optional[User]:
        # Get current user from context
        current_user = info.context.get("user")
        if not current_user:
            return None
        return User(**current_user)

@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def login(self, input: LoginInput) -> AuthPayload:
        from backend.modules.auth.service import auth_service
        result = await auth_service.login_user(input.email, input.password)
        return AuthPayload(**result)
    
    @strawberry.mutation
    async def register(self, input: RegisterInput) -> AuthPayload:
        from backend.modules.auth.service import auth_service
        result = await auth_service.register_user(
            input.email, 
            input.password, 
            {"full_name": input.full_name}
        )
        return AuthPayload(**result)
    
    @strawberry.mutation
    async def refresh_token(self, refresh_token: str) -> AuthPayload:
        from backend.modules.auth.service import auth_service
        result = await auth_service.refresh_token(refresh_token)
        return AuthPayload(**result)
```

#### 2.3 Trading GraphQL Schema

```python
# backend/graphql/trading.py
import strawberry
from typing import List, Optional
from decimal import Decimal
from datetime import datetime

@strawberry.type
class Position:
    ticket: int
    symbol: str
    type: str
    volume: float
    open_price: float
    current_price: float
    sl: float
    tp: float
    profit: float
    open_time: datetime

@strawberry.type
class Signal:
    id: str
    symbol: str
    signal_type: str
    direction: str
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime

@strawberry.input
class OrderInput:
    symbol: str
    order_type: str
    volume: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    comment: Optional[str] = None

@strawberry.type
class TradingQuery:
    @strawberry.field
    async def positions(self, info) -> List[Position]:
        # Implement position fetching
        pass
    
    @strawberry.field
    async def signals(self, info) -> List[Signal]:
        # Implement signal fetching
        pass
    
    @strawberry.field
    async def account_info(self, info) -> dict:
        # Implement account info fetching
        pass

@strawberry.type
class TradingMutation:
    @strawberry.mutation
    async def place_order(self, input: OrderInput, info) -> dict:
        # Implement order placement
        pass
    
    @strawberry.mutation
    async def close_position(self, ticket: int, info) -> dict:
        # Implement position closing
        pass
```

---

### Phase 3: Enhanced Security Implementation

#### 3.1 Rate Limiting & API Protection

```python
# backend/security/rate_limiter.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException
import redis

# Initialize Redis for rate limiting
redis_client = redis.Redis(host='localhost', port=6379, db=1)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/1"
)

# Custom rate limit exceeded handler
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    response = HTTPException(
        status_code=429,
        detail={
            "error": "Rate limit exceeded",
            "detail": f"You have exceeded the rate limit of {exc.detail}",
            "retry_after": exc.retry_after
        }
    )
    return response

# Rate limiting decorators
def rate_limit_auth(requests: int = 5, window: int = 60):
    """Rate limit for auth endpoints"""
    return limiter.limit(f"{requests}/minute")

def rate_limit_trading(requests: int = 100, window: int = 60):
    """Rate limit for trading endpoints"""
    return limiter.limit(f"{requests}/minute")

def rate_limit_data(requests: int = 1000, window: int = 60):
    """Rate limit for data endpoints"""
    return limiter.limit(f"{requests}/minute")
```

#### 3.2 Input Validation & Sanitization

```python
# backend/security/validation.py
from pydantic import BaseModel, validator, Field
from typing import Optional, List
import re
from decimal import Decimal

class TradingOrderRequest(BaseModel):
    symbol: str = Field(..., regex=r'^[A-Z]{6}$', description="6-character symbol")
    order_type: str = Field(..., regex=r'^(buy|sell)$')
    volume: Decimal = Field(..., gt=0, le=100, description="Order volume")
    sl: Optional[Decimal] = Field(None, gt=0)
    tp: Optional[Decimal] = Field(None, gt=0)
    comment: Optional[str] = Field(None, max_length=100)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        allowed_symbols = ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'BTCUSD']
        if v not in allowed_symbols:
            raise ValueError(f'Symbol must be one of: {allowed_symbols}')
        return v
    
    @validator('comment')
    def sanitize_comment(cls, v):
        if v:
            # Remove potentially dangerous characters
            v = re.sub(r'[<>"\';]', '', v)
        return v

class SignalRequest(BaseModel):
    symbol: str = Field(..., regex=r'^[A-Z]{6}$')
    timeframe: str = Field(..., regex=r'^(M1|M5|M15|M30|H1|H4|D1)$')
    signal_type: str = Field(..., regex=r'^(ORDER_BLOCK|FAIR_VALUE_GAP|BREAKER_BLOCK)$')
```

#### 3.3 CORS & Security Headers

```python
# backend/security/cors.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import os

def setup_cors(app):
    """Setup CORS with proper security"""
    
    # Environment-specific origins
    if os.getenv("ENVIRONMENT") == "production":
        allowed_origins = [
            "https://your-domain.com",
            "https://www.your-domain.com"
        ]
    else:
        allowed_origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count"]
    )
    
    # Add security headers
    @app.middleware("http")
    async def add_security_headers(request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response
    
    # Trusted hosts (production only)
    if os.getenv("ENVIRONMENT") == "production":
        app.add_middleware(
            TrustedHostMiddleware, 
            allowed_hosts=["your-domain.com", "*.your-domain.com"]
        )
        app.add_middleware(HTTPSRedirectMiddleware)
```

#### 3.4 API Key Management

```python
# backend/security/api_keys.py
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Boolean, Integer
from backend.core.database import Base

security = HTTPBearer()

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    key_hash = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class APIKeyManager:
    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key"""
        return f"aat_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    async def create_api_key(user_id: str, name: str, expires_in_days: int = 365) -> str:
        """Create new API key for user"""
        api_key = APIKeyManager.generate_api_key()
        key_hash = APIKeyManager.hash_api_key(api_key)
        
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Save to database (implement with your DB session)
        # ...
        
        return api_key
    
    @staticmethod
    async def verify_api_key(api_key: str) -> dict:
        """Verify API key and return user info"""
        key_hash = APIKeyManager.hash_api_key(api_key)
        
        # Query database for key (implement with your DB session)
        # ...
        
        # Update last_used timestamp
        # ...
        
        return {"user_id": "user_id", "permissions": []}

async def get_api_key_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get user from API key"""
    if not credentials.credentials.startswith("aat_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    user_info = await APIKeyManager.verify_api_key(credentials.credentials)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return user_info
```

---

### Phase 4: Environment Configuration

#### 4.1 Updated Environment Variables

```bash
# .env.example
# Database
DATABASE_URL=sqlite+aiosqlite:///./ai_algo_trade.db

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# Rate Limiting Redis
RATE_LIMIT_REDIS_URL=redis://localhost:6379/1

# Security
ENVIRONMENT=development
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# MetaTrader 5 (keep encrypted)
MT5_LOGIN=
MT5_PASSWORD=
MT5_SERVER=

# External APIs
OPENAI_API_KEY=
GEMINI_API_KEY=

# Monitoring
SENTRY_DSN=
LOG_LEVEL=INFO
```

#### 4.2 Updated Settings

```python
# backend/core/config/settings.py (Updated)
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Supabase settings
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Enhanced security settings
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Rate limiting
    RATE_LIMIT_REDIS_URL: str = "redis://localhost:6379/1"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Environment
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
```

---

### Phase 5: Frontend Integration

#### 5.1 Supabase Client Setup

```typescript
// frontend/lib/supabase.ts
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Auth helpers
export const signUp = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signUp({
    email,
    password,
  })
  return { data, error }
}

export const signIn = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  })
  return { data, error }
}

export const signOut = async () => {
  const { error } = await supabase.auth.signOut()
  return { error }
}
```

#### 5.2 GraphQL Client Setup

```typescript
// frontend/lib/graphql.ts
import { GraphQLClient } from 'graphql-request'
import { supabase } from './supabase'

const graphqlEndpoint = process.env.NEXT_PUBLIC_API_URL + '/graphql'

export const graphqlClient = new GraphQLClient(graphqlEndpoint, {
  requestMiddleware: async (request) => {
    const { data: { session } } = await supabase.auth.getSession()
    
    if (session?.access_token) {
      request.headers = {
        ...request.headers,
        Authorization: `Bearer ${session.access_token}`,
      }
    }
    
    return request
  },
})

// Example queries
export const GET_USER_PROFILE = gql`
  query GetUserProfile {
    me {
      id
      email
      fullName
      role
      subscriptionPlan
    }
  }
`

export const GET_TRADING_POSITIONS = gql`
  query GetPositions {
    positions {
      ticket
      symbol
      type
      volume
      openPrice
      currentPrice
      profit
    }
  }
`
```

#### 5.3 Authentication Context

```typescript
// frontend/contexts/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '../lib/supabase'

interface AuthContextType {
  user: User | null
  session: Session | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<any>
  signUp: (email: string, password: string) => Promise<any>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Get initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for auth changes
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session)
      setUser(session?.user ?? null)
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    return { data, error }
  }

  const signUp = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    return { data, error }
  }

  const signOut = async () => {
    await supabase.auth.signOut()
  }

  return (
    <AuthContext.Provider value={{
      user,
      session,
      loading,
      signIn,
      signUp,
      signOut,
    }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

---

## 🚀 Implementation Timeline

### Week 1: Foundation Setup
- [ ] Supabase project setup
- [ ] Authentication module structure
- [ ] Basic user models and database schema
- [ ] Environment configuration

### Week 2: Core Authentication
- [ ] Supabase integration
- [ ] JWT middleware
- [ ] Registration/login endpoints
- [ ] Password reset functionality

### Week 3: GraphQL Integration
- [ ] Strawberry GraphQL setup
- [ ] Authentication schema
- [ ] Trading schema
- [ ] GraphQL playground

### Week 4: Security Implementation
- [ ] Rate limiting
- [ ] Input validation
- [ ] API key management
- [ ] Security headers and CORS

### Week 5: Frontend Integration
- [ ] Supabase client setup
- [ ] GraphQL client
- [ ] Authentication context
- [ ] Protected routes

### Week 6: Testing & Optimization
- [ ] Unit tests
- [ ] Integration tests
- [ ] Security testing
- [ ] Performance optimization

---

## 📋 Security Checklist

### Authentication Security
- [ ] Secure password requirements
- [ ] Email verification
- [ ] Two-factor authentication (optional)
- [ ] Account lockout after failed attempts
- [ ] Secure session management

### API Security
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection

### Infrastructure Security
- [ ] HTTPS enforcement
- [ ] Secure headers
- [ ] Environment variable protection
- [ ] Database connection security
- [ ] API key rotation

### Monitoring & Logging
- [ ] Authentication logs
- [ ] Failed login attempts
- [ ] API usage monitoring
- [ ] Error tracking
- [ ] Security incident alerts

---

## 🔧 Required Dependencies

### Backend Dependencies
```python
# requirements.txt additions
supabase==2.0.0
strawberry-graphql[fastapi]==0.205.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9
redis==5.0.1
pydantic[email]==2.5.0
python-multipart==0.0.6
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "@supabase/supabase-js": "^2.38.0",
    "graphql-request": "^6.1.0",
    "@apollo/client": "^3.8.7",
    "graphql": "^16.8.1"
  }
}
```

---

## 🎯 Expected Outcomes

### Security Improvements
- **99%** reduction in unauthorized access
- **100%** of API endpoints protected
- **Real-time** threat detection and response
- **Enterprise-grade** authentication system

### User Experience
- **Single sign-on** across all features
- **Seamless** authentication flow
- **Progressive** user onboarding
- **Personalized** trading preferences

### Developer Experience
- **Type-safe** GraphQL API
- **Comprehensive** authentication system
- **Scalable** architecture
- **Maintainable** codebase

### Performance Benefits
- **Faster** API responses with GraphQL
- **Reduced** bandwidth usage
- **Optimized** database queries
- **Cached** authentication states

---

This implementation plan provides a comprehensive roadmap for integrating Supabase authentication, GraphQL API, and enhanced security measures into your AI algorithmic trading platform. The modular approach ensures maintainability while the security-first design protects against common vulnerabilities.

Would you like me to start implementing any specific phase or module?
