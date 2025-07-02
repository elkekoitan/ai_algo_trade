import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from fastapi import HTTPException, status
from supabase import Client
from backend.core.config.supabase_config import get_supabase_client, get_supabase_admin
import hashlib
import secrets
from cryptography.fernet import Fernet
import re

logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    id: str
    email: Optional[str]
    phone: Optional[str]
    full_name: Optional[str]
    avatar_url: Optional[str]
    role: str
    subscription_plan: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    mt5_accounts: List[Dict[str, Any]]
    trading_preferences: Dict[str, Any]

@dataclass
class MT5Account:
    login: str
    server: str
    password_encrypted: str
    account_type: str
    currency: str
    balance: float
    equity: float
    margin: float
    free_margin: float
    is_active: bool
    last_sync: datetime

@dataclass
class AuthResponse:
    access_token: str
    refresh_token: str
    user: UserProfile
    expires_in: int
    token_type: str = "bearer"

class SupabaseAuthService:
    def __init__(self):
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin()
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for MT5 credentials"""
        try:
            # Try to get from environment or generate new
            key = Fernet.generate_key()
            return key
        except Exception as e:
            logger.error(f"Failed to get encryption key: {e}")
            return Fernet.generate_key()
    
    async def register_with_email(self, email: str, password: str, 
                                 full_name: Optional[str] = None,
                                 phone: Optional[str] = None) -> AuthResponse:
        """Register user with email and password"""
        try:
            # Validate email format
            if not self._validate_email(email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
            
            # Validate password strength
            if not self._validate_password(password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters with uppercase, lowercase, number and special character"
                )
            
            # Register with Supabase Auth
            response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "phone": phone,
                        "role": "user",
                        "subscription_plan": "free"
                    }
                }
            })
            
            if response.user:
                # Create user profile in database
                await self._create_user_profile(response.user, {
                    "full_name": full_name,
                    "phone": phone
                })
                
                # Create user profile response
                user_profile = await self._get_user_profile(response.user.id)
                
                return AuthResponse(
                    access_token=response.session.access_token if response.session else "",
                    refresh_token=response.session.refresh_token if response.session else "",
                    user=user_profile,
                    expires_in=response.session.expires_in if response.session else 3600
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed"
                )
                
        except Exception as e:
            logger.error(f"Email registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def register_with_phone(self, phone: str, password: str,
                                 full_name: Optional[str] = None) -> Dict[str, Any]:
        """Register user with phone number"""
        try:
            # Validate phone format
            if not self._validate_phone(phone):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number format"
                )
            
            # Register with Supabase Auth using phone
            response = self.client.auth.sign_up({
                "phone": phone,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "role": "user",
                        "subscription_plan": "free"
                    }
                }
            })
            
            return {
                "message": "OTP sent to phone number",
                "phone": phone,
                "requires_verification": True
            }
            
        except Exception as e:
            logger.error(f"Phone registration failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone registration failed: {str(e)}"
            )
    
    async def verify_phone_otp(self, phone: str, otp: str) -> AuthResponse:
        """Verify phone OTP and complete registration"""
        try:
            response = self.client.auth.verify_otp({
                "phone": phone,
                "token": otp,
                "type": "sms"
            })
            
            if response.user:
                # Create user profile
                await self._create_user_profile(response.user, {
                    "phone": phone
                })
                
                user_profile = await self._get_user_profile(response.user.id)
                
                return AuthResponse(
                    access_token=response.session.access_token if response.session else "",
                    refresh_token=response.session.refresh_token if response.session else "",
                    user=user_profile,
                    expires_in=response.session.expires_in if response.session else 3600
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP verification failed"
                )
                
        except Exception as e:
            logger.error(f"OTP verification failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OTP verification failed: {str(e)}"
            )
    
    async def login_with_email(self, email: str, password: str) -> AuthResponse:
        """Login with email and password"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                # Update last login
                await self._update_last_login(response.user.id)
                
                user_profile = await self._get_user_profile(response.user.id)
                
                return AuthResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    user=user_profile,
                    expires_in=response.session.expires_in
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
                
        except Exception as e:
            logger.error(f"Email login failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    
    async def login_with_phone(self, phone: str, password: str) -> AuthResponse:
        """Login with phone and password"""
        try:
            response = self.client.auth.sign_in_with_password({
                "phone": phone,
                "password": password
            })
            
            if response.user and response.session:
                await self._update_last_login(response.user.id)
                user_profile = await self._get_user_profile(response.user.id)
                
                return AuthResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    user=user_profile,
                    expires_in=response.session.expires_in
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid phone or password"
                )
                
        except Exception as e:
            logger.error(f"Phone login failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid phone or password"
            )
    
    async def login_with_mt5(self, mt5_login: str, mt5_password: str, 
                            mt5_server: str) -> AuthResponse:
        """Login with MT5 account credentials"""
        try:
            # First verify MT5 credentials
            mt5_verified = await self._verify_mt5_credentials(mt5_login, mt5_password, mt5_server)
            
            if not mt5_verified:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MT5 credentials"
                )
            
            # Check if user exists with this MT5 account
            user_profile = await self._get_user_by_mt5_account(mt5_login, mt5_server)
            
            if user_profile:
                # Generate session token for MT5 login
                session_token = self._generate_session_token(user_profile.id)
                
                return AuthResponse(
                    access_token=session_token,
                    refresh_token=session_token,
                    user=user_profile,
                    expires_in=3600
                )
            else:
                # Create new user with MT5 account
                user_id = await self._create_user_from_mt5(mt5_login, mt5_password, mt5_server)
                user_profile = await self._get_user_profile(user_id)
                
                session_token = self._generate_session_token(user_id)
                
                return AuthResponse(
                    access_token=session_token,
                    refresh_token=session_token,
                    user=user_profile,
                    expires_in=3600
                )
                
        except Exception as e:
            logger.error(f"MT5 login failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"MT5 login failed: {str(e)}"
            )
    
    async def add_mt5_account(self, user_id: str, mt5_login: str, 
                             mt5_password: str, mt5_server: str) -> Dict[str, Any]:
        """Add MT5 account to existing user"""
        try:
            # Verify MT5 credentials
            mt5_verified = await self._verify_mt5_credentials(mt5_login, mt5_password, mt5_server)
            
            if not mt5_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid MT5 credentials"
                )
            
            # Encrypt MT5 password
            encrypted_password = self.fernet.encrypt(mt5_password.encode()).decode()
            
            # Get MT5 account info
            mt5_info = await self._get_mt5_account_info(mt5_login, mt5_server)
            
            # Store MT5 account
            mt5_account_data = {
                "user_id": user_id,
                "mt5_login": mt5_login,
                "mt5_server": mt5_server,
                "mt5_password_encrypted": encrypted_password,
                "account_type": mt5_info.get("account_type", "unknown"),
                "currency": mt5_info.get("currency", "USD"),
                "balance": mt5_info.get("balance", 0.0),
                "equity": mt5_info.get("equity", 0.0),
                "margin": mt5_info.get("margin", 0.0),
                "free_margin": mt5_info.get("free_margin", 0.0),
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_sync": datetime.utcnow().isoformat()
            }
            
            # Insert into database
            result = self.admin_client.table("mt5_accounts").insert(mt5_account_data).execute()
            
            return {
                "message": "MT5 account added successfully",
                "mt5_account": {
                    "login": mt5_login,
                    "server": mt5_server,
                    "account_type": mt5_info.get("account_type"),
                    "currency": mt5_info.get("currency"),
                    "balance": mt5_info.get("balance")
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to add MT5 account: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to add MT5 account: {str(e)}"
            )
    
    async def get_user_mt5_accounts(self, user_id: str) -> List[MT5Account]:
        """Get all MT5 accounts for user"""
        try:
            result = self.admin_client.table("mt5_accounts").select("*").eq("user_id", user_id).execute()
            
            mt5_accounts = []
            for account_data in result.data:
                # Decrypt password
                encrypted_password = account_data["mt5_password_encrypted"]
                
                mt5_account = MT5Account(
                    login=account_data["mt5_login"],
                    server=account_data["mt5_server"],
                    password_encrypted=encrypted_password,
                    account_type=account_data.get("account_type", "unknown"),
                    currency=account_data.get("currency", "USD"),
                    balance=account_data.get("balance", 0.0),
                    equity=account_data.get("equity", 0.0),
                    margin=account_data.get("margin", 0.0),
                    free_margin=account_data.get("free_margin", 0.0),
                    is_active=account_data.get("is_active", True),
                    last_sync=datetime.fromisoformat(account_data.get("last_sync", datetime.utcnow().isoformat()))
                )
                mt5_accounts.append(mt5_account)
            
            return mt5_accounts
            
        except Exception as e:
            logger.error(f"Failed to get MT5 accounts: {e}")
            return []
    
    async def verify_token(self, token: str) -> Optional[UserProfile]:
        """Verify access token and return user profile"""
        try:
            # Get user from token
            response = self.client.auth.get_user(token)
            
            if response.user:
                user_profile = await self._get_user_profile(response.user.id)
                return user_profile
            else:
                return None
                
        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> AuthResponse:
        """Refresh access token"""
        try:
            response = self.client.auth.refresh_session(refresh_token)
            
            if response.session and response.user:
                user_profile = await self._get_user_profile(response.user.id)
                
                return AuthResponse(
                    access_token=response.session.access_token,
                    refresh_token=response.session.refresh_token,
                    user=user_profile,
                    expires_in=response.session.expires_in
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
                
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    async def logout(self, token: str) -> bool:
        """Logout user"""
        try:
            self.client.auth.sign_out(token)
            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    # Helper methods
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's between 10-15 digits
        return 10 <= len(digits_only) <= 15
    
    def _validate_password(self, password: str) -> bool:
        """Validate password strength"""
        if len(password) < 8:
            return False
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        return has_upper and has_lower and has_digit and has_special
    
    async def _verify_mt5_credentials(self, login: str, password: str, server: str) -> bool:
        """Verify MT5 credentials with MT5 server"""
        try:
            # This would integrate with your MT5 service
            # For now, return True for demo credentials
            demo_credentials = {
                "25201110": {"password": "e|([rXU1IsiM", "server": "Tickmill-Demo"}
            }
            
            if login in demo_credentials:
                expected = demo_credentials[login]
                return (password == expected["password"] and 
                       server == expected["server"])
            
            # For other accounts, you would make actual MT5 connection
            return True  # Placeholder
            
        except Exception as e:
            logger.error(f"MT5 verification failed: {e}")
            return False
    
    async def _get_mt5_account_info(self, login: str, server: str) -> Dict[str, Any]:
        """Get MT5 account information"""
        try:
            # This would connect to MT5 and get account info
            # For now, return mock data
            return {
                "account_type": "Demo" if "demo" in server.lower() else "Real",
                "currency": "USD",
                "balance": 10000.0,
                "equity": 10000.0,
                "margin": 0.0,
                "free_margin": 10000.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get MT5 account info: {e}")
            return {}
    
    async def _create_user_profile(self, user: Any, additional_data: Dict[str, Any]):
        """Create user profile in database"""
        try:
            profile_data = {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "full_name": additional_data.get("full_name"),
                "avatar_url": user.user_metadata.get("avatar_url"),
                "role": additional_data.get("role", "user"),
                "subscription_plan": additional_data.get("subscription_plan", "free"),
                "is_active": True,
                "is_verified": user.email_confirmed_at is not None or user.phone_confirmed_at is not None,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "trading_preferences": {},
                "api_settings": {}
            }
            
            result = self.admin_client.table("user_profiles").insert(profile_data).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Failed to create user profile: {e}")
            return None
    
    async def _get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile from database"""
        try:
            result = self.admin_client.table("user_profiles").select("*").eq("id", user_id).execute()
            
            if result.data:
                profile_data = result.data[0]
                
                # Get MT5 accounts
                mt5_accounts = await self.get_user_mt5_accounts(user_id)
                mt5_accounts_data = [
                    {
                        "login": acc.login,
                        "server": acc.server,
                        "account_type": acc.account_type,
                        "currency": acc.currency,
                        "balance": acc.balance,
                        "is_active": acc.is_active
                    }
                    for acc in mt5_accounts
                ]
                
                return UserProfile(
                    id=profile_data["id"],
                    email=profile_data.get("email"),
                    phone=profile_data.get("phone"),
                    full_name=profile_data.get("full_name"),
                    avatar_url=profile_data.get("avatar_url"),
                    role=profile_data.get("role", "user"),
                    subscription_plan=profile_data.get("subscription_plan", "free"),
                    is_active=profile_data.get("is_active", True),
                    is_verified=profile_data.get("is_verified", False),
                    created_at=datetime.fromisoformat(profile_data.get("created_at", datetime.utcnow().isoformat())),
                    last_login=datetime.fromisoformat(profile_data["last_login"]) if profile_data.get("last_login") else None,
                    mt5_accounts=mt5_accounts_data,
                    trading_preferences=profile_data.get("trading_preferences", {})
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )
                
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get user profile"
            )
    
    async def _get_user_by_mt5_account(self, mt5_login: str, mt5_server: str) -> Optional[UserProfile]:
        """Get user by MT5 account"""
        try:
            result = self.admin_client.table("mt5_accounts").select("user_id").eq("mt5_login", mt5_login).eq("mt5_server", mt5_server).execute()
            
            if result.data:
                user_id = result.data[0]["user_id"]
                return await self._get_user_profile(user_id)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user by MT5 account: {e}")
            return None
    
    async def _create_user_from_mt5(self, mt5_login: str, mt5_password: str, mt5_server: str) -> str:
        """Create new user from MT5 credentials"""
        try:
            # Generate user ID
            user_id = f"mt5_{mt5_login}_{int(datetime.utcnow().timestamp())}"
            
            # Create user profile
            profile_data = {
                "id": user_id,
                "email": None,
                "phone": None,
                "full_name": f"MT5 User {mt5_login}",
                "role": "user",
                "subscription_plan": "free",
                "is_active": True,
                "is_verified": True,  # MT5 verification counts as verification
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat(),
                "trading_preferences": {},
                "api_settings": {}
            }
            
            self.admin_client.table("user_profiles").insert(profile_data).execute()
            
            # Add MT5 account
            await self.add_mt5_account(user_id, mt5_login, mt5_password, mt5_server)
            
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to create user from MT5: {e}")
            raise
    
    async def _update_last_login(self, user_id: str):
        """Update user's last login timestamp"""
        try:
            self.admin_client.table("user_profiles").update({
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Failed to update last login: {e}")
    
    def _generate_session_token(self, user_id: str) -> str:
        """Generate session token for MT5 users"""
        try:
            # Create a simple session token
            timestamp = int(datetime.utcnow().timestamp())
            data = f"{user_id}:{timestamp}:{secrets.token_hex(16)}"
            return hashlib.sha256(data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to generate session token: {e}")
            return secrets.token_hex(32)

# Global instance
supabase_auth_service = SupabaseAuthService() 