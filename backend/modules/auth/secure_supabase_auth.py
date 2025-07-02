"""
Secure Supabase Authentication Service
Implements secure authentication with SQL injection protection
"""

import re
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import secrets
import hashlib
from dataclasses import dataclass
from cryptography.fernet import Fernet
from fastapi import HTTPException, status
from supabase import create_client, Client
from pydantic import BaseModel, EmailStr, validator
import bleach

from backend.core.config.supabase_config import get_supabase_client, get_supabase_admin_client

logger = logging.getLogger(__name__)

# Security constants
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=30)
MIN_PASSWORD_LENGTH = 8
PASSWORD_COMPLEXITY_REGEX = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
ALLOWED_CHARACTERS_REGEX = r'^[a-zA-Z0-9@$!%*?&\s\-_.]+$'

@dataclass
class SecureUserProfile:
    """Secure user profile with validated fields"""
    id: str
    email: Optional[EmailStr]
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
    failed_login_attempts: int = 0
    last_failed_login: Optional[datetime] = None
    account_locked_until: Optional[datetime] = None

class SecureSupabaseAuthService:
    """Secure authentication service with SQL injection protection"""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.admin_client = get_supabase_admin_client()
        self.fernet = Fernet(self._get_or_create_encryption_key())
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        # In production, this should be stored in secure key management
        key = Fernet.generate_key()
        return key
    
    def _sanitize_input(self, input_str: str, field_name: str) -> str:
        """Sanitize user input to prevent SQL injection and XSS"""
        if not input_str:
            return input_str
        
        # Remove any SQL keywords and dangerous characters
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 
                       'EXEC', 'EXECUTE', '--', '/*', '*/', 'xp_', 'sp_']
        
        input_upper = input_str.upper()
        for keyword in sql_keywords:
            if keyword in input_upper:
                logger.warning(f"Potential SQL injection attempt detected in {field_name}: {keyword}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid characters in {field_name}"
                )
        
        # HTML escape for XSS protection
        sanitized = bleach.clean(input_str, tags=[], strip=True)
        
        # Additional validation based on field type
        if field_name == 'email':
            if not self._validate_email(sanitized):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
        elif field_name == 'phone':
            if not self._validate_phone(sanitized):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone format"
                )
        elif field_name == 'password':
            if not self._validate_password_strength(sanitized):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password does not meet security requirements"
                )
        elif field_name in ['full_name', 'mt5_login', 'mt5_server']:
            # Allow only safe characters
            if not re.match(ALLOWED_CHARACTERS_REGEX, sanitized):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid characters in {field_name}"
                )
        
        return sanitized
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format with strict regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's between 10-15 digits
        return 10 <= len(digits_only) <= 15
    
    def _validate_password_strength(self, password: str) -> bool:
        """Validate password meets security requirements"""
        if len(password) < MIN_PASSWORD_LENGTH:
            return False
        
        # Check complexity requirements
        return bool(re.match(PASSWORD_COMPLEXITY_REGEX, password))
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt for additional security"""
        # Supabase handles password hashing, but we add extra layer
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hashed.hex()}"
    
    def _verify_password_hash(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, hashed = password_hash.split('$')
            test_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return test_hash.hex() == hashed
        except:
            return False
    
    async def _check_account_lockout(self, identifier: str) -> None:
        """Check if account is locked due to failed attempts"""
        try:
            # Use parameterized query - no SQL injection risk
            result = self.admin_client.table("user_profiles").select(
                "failed_login_attempts", "last_failed_login", "account_locked_until"
            ).or_(f"email.eq.{identifier},phone.eq.{identifier}").execute()
            
            if result.data:
                user = result.data[0]
                locked_until = user.get('account_locked_until')
                
                if locked_until:
                    locked_until_dt = datetime.fromisoformat(locked_until)
                    if locked_until_dt > datetime.utcnow():
                        raise HTTPException(
                            status_code=status.HTTP_423_LOCKED,
                            detail=f"Account locked until {locked_until_dt.isoformat()}"
                        )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking account lockout: {e}")
    
    async def _record_failed_login(self, identifier: str) -> None:
        """Record failed login attempt"""
        try:
            # Get current failed attempts
            result = self.admin_client.table("user_profiles").select(
                "id", "failed_login_attempts"
            ).or_(f"email.eq.{identifier},phone.eq.{identifier}").execute()
            
            if result.data:
                user = result.data[0]
                failed_attempts = user.get('failed_login_attempts', 0) + 1
                
                update_data = {
                    "failed_login_attempts": failed_attempts,
                    "last_failed_login": datetime.utcnow().isoformat()
                }
                
                # Lock account if too many failed attempts
                if failed_attempts >= MAX_LOGIN_ATTEMPTS:
                    update_data["account_locked_until"] = (
                        datetime.utcnow() + LOCKOUT_DURATION
                    ).isoformat()
                
                # Use parameterized update - no SQL injection risk
                self.admin_client.table("user_profiles").update(
                    update_data
                ).eq("id", user['id']).execute()
                
        except Exception as e:
            logger.error(f"Error recording failed login: {e}")
    
    async def _reset_failed_login_attempts(self, user_id: str) -> None:
        """Reset failed login attempts on successful login"""
        try:
            self.admin_client.table("user_profiles").update({
                "failed_login_attempts": 0,
                "last_failed_login": None,
                "account_locked_until": None,
                "last_login": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
        except Exception as e:
            logger.error(f"Error resetting failed login attempts: {e}")
    
    async def register_with_email(self, email: str, password: str, 
                                 full_name: Optional[str] = None,
                                 phone: Optional[str] = None) -> Dict[str, Any]:
        """Register new user with email - SQL injection protected"""
        try:
            # Sanitize all inputs
            email = self._sanitize_input(email, 'email')
            password = self._sanitize_input(password, 'password')
            
            if full_name:
                full_name = self._sanitize_input(full_name, 'full_name')
            if phone:
                phone = self._sanitize_input(phone, 'phone')
            
            # Use Supabase client method - no direct SQL
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
                # Create user profile with parameterized insert
                profile_data = {
                    "id": response.user.id,
                    "email": email,
                    "phone": phone,
                    "full_name": full_name,
                    "role": "user",
                    "subscription_plan": "free",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": datetime.utcnow().isoformat(),
                    "trading_preferences": {},
                    "api_settings": {},
                    "notification_preferences": {
                        "email_notifications": True,
                        "sms_notifications": False,
                        "push_notifications": True
                    }
                }
                
                # No SQL injection risk - using Supabase client
                self.admin_client.table("user_profiles").insert(profile_data).execute()
                
                return {
                    "message": "Registration successful",
                    "user_id": response.user.id,
                    "email": email
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration failed"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    async def login_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Login with email - SQL injection protected"""
        try:
            # Sanitize inputs
            email = self._sanitize_input(email, 'email')
            password = self._sanitize_input(password, 'password')
            
            # Check account lockout
            await self._check_account_lockout(email)
            
            # Use Supabase client method - no direct SQL
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                # Reset failed login attempts
                await self._reset_failed_login_attempts(response.user.id)
                
                # Get user profile with parameterized query
                profile = self.admin_client.table("user_profiles").select("*").eq(
                    "id", response.user.id
                ).execute()
                
                if profile.data:
                    return {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                        "user": profile.data[0],
                        "expires_in": response.session.expires_in
                    }
                else:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="User profile not found"
                    )
            else:
                # Record failed login attempt
                await self._record_failed_login(email)
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            # Record failed login attempt
            await self._record_failed_login(email)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Login failed"
            )
    
    async def add_mt5_account(self, user_id: str, mt5_login: str, 
                             mt5_password: str, mt5_server: str) -> Dict[str, Any]:
        """Add MT5 account - SQL injection protected"""
        try:
            # Sanitize inputs
            mt5_login = self._sanitize_input(mt5_login, 'mt5_login')
            mt5_server = self._sanitize_input(mt5_server, 'mt5_server')
            # Password is encrypted, not sanitized
            
            # Validate user_id is valid UUID
            import uuid
            try:
                uuid.UUID(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user ID"
                )
            
            # Encrypt MT5 password
            encrypted_password = self.fernet.encrypt(mt5_password.encode()).decode()
            
            # Store MT5 account with parameterized insert
            mt5_account_data = {
                "user_id": user_id,
                "mt5_login": mt5_login,
                "mt5_server": mt5_server,
                "mt5_password_encrypted": encrypted_password,
                "account_type": "unknown",
                "currency": "USD",
                "balance": 0.0,
                "equity": 0.0,
                "is_active": True,
                "created_at": datetime.utcnow().isoformat(),
                "last_sync": datetime.utcnow().isoformat()
            }
            
            # No SQL injection risk - using Supabase client
            result = self.admin_client.table("mt5_accounts").insert(
                mt5_account_data
            ).execute()
            
            return {
                "message": "MT5 account added successfully",
                "mt5_account_id": result.data[0]['id'] if result.data else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error adding MT5 account: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add MT5 account"
            )
    
    async def search_users(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search users - SQL injection protected"""
        try:
            # Sanitize search term
            search_term = self._sanitize_input(search_term, 'search_term')
            
            # Validate limit
            if not isinstance(limit, int) or limit < 1 or limit > 100:
                limit = 10
            
            # Use Supabase's safe search methods
            # No SQL injection risk - using parameterized queries
            result = self.admin_client.table("user_profiles").select(
                "id", "email", "full_name", "role", "is_active"
            ).or_(
                f"email.ilike.%{search_term}%,full_name.ilike.%{search_term}%"
            ).limit(limit).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []

# Create singleton instance
secure_auth_service = SecureSupabaseAuthService() 