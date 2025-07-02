from fastapi import APIRouter, HTTPException, Depends, status, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
import logging
import datetime
from backend.modules.auth.supabase_auth import supabase_auth_service, UserProfile, AuthResponse

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Pydantic models
class EmailRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    phone: Optional[str] = None

class PhoneRegisterRequest(BaseModel):
    phone: str = Field(..., regex=r'^\+?[1-9]\d{1,14}$')
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str

class PhoneLoginRequest(BaseModel):
    phone: str
    password: str

class MT5LoginRequest(BaseModel):
    mt5_login: str
    mt5_password: str
    mt5_server: str

class OTPVerificationRequest(BaseModel):
    phone: str
    otp: str

class AddMT5AccountRequest(BaseModel):
    mt5_login: str
    mt5_password: str
    mt5_server: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserProfile:
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    user = await supabase_auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    return user

# Registration endpoints
@router.post("/register/email", response_model=AuthResponse)
async def register_with_email(request: EmailRegisterRequest):
    """Register new user with email and password"""
    try:
        return await supabase_auth_service.register_with_email(
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            phone=request.phone
        )
    except Exception as e:
        logger.error(f"Email registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/register/phone")
async def register_with_phone(request: PhoneRegisterRequest):
    """Register new user with phone number"""
    try:
        return await supabase_auth_service.register_with_phone(
            phone=request.phone,
            password=request.password,
            full_name=request.full_name
        )
    except Exception as e:
        logger.error(f"Phone registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify/phone", response_model=AuthResponse)
async def verify_phone_otp(request: OTPVerificationRequest):
    """Verify phone number with OTP"""
    try:
        return await supabase_auth_service.verify_phone_otp(
            phone=request.phone,
            otp=request.otp
        )
    except Exception as e:
        logger.error(f"OTP verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Login endpoints
@router.post("/login/email", response_model=AuthResponse)
async def login_with_email(request: EmailLoginRequest):
    """Login with email and password"""
    try:
        return await supabase_auth_service.login_with_email(
            email=request.email,
            password=request.password
        )
    except Exception as e:
        logger.error(f"Email login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

@router.post("/login/phone", response_model=AuthResponse)
async def login_with_phone(request: PhoneLoginRequest):
    """Login with phone and password"""
    try:
        return await supabase_auth_service.login_with_phone(
            phone=request.phone,
            password=request.password
        )
    except Exception as e:
        logger.error(f"Phone login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid phone or password"
        )

@router.post("/login/mt5", response_model=AuthResponse)
async def login_with_mt5(request: MT5LoginRequest):
    """Login with MT5 account credentials"""
    try:
        return await supabase_auth_service.login_with_mt5(
            mt5_login=request.mt5_login,
            mt5_password=request.mt5_password,
            mt5_server=request.mt5_server
        )
    except Exception as e:
        logger.error(f"MT5 login failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MT5 credentials"
        )

# Token management
@router.post("/refresh", response_model=AuthResponse)
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        return await supabase_auth_service.refresh_token(request.refresh_token)
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout current user"""
    try:
        success = await supabase_auth_service.logout(credentials.credentials)
        return {"message": "Logged out successfully" if success else "Logout failed"}
    except Exception as e:
        logger.error(f"Logout failed: {e}")
        return {"message": "Logout completed"}

# User profile endpoints
@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.post("/mt5/add")
async def add_mt5_account(
    request: AddMT5AccountRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """Add MT5 account to current user"""
    try:
        return await supabase_auth_service.add_mt5_account(
            user_id=current_user.id,
            mt5_login=request.mt5_login,
            mt5_password=request.mt5_password,
            mt5_server=request.mt5_server
        )
    except Exception as e:
        logger.error(f"Failed to add MT5 account: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/mt5/accounts")
async def get_mt5_accounts(current_user: UserProfile = Depends(get_current_user)):
    """Get all MT5 accounts for current user"""
    try:
        mt5_accounts = await supabase_auth_service.get_user_mt5_accounts(current_user.id)
        return {
            "mt5_accounts": [
                {
                    "login": acc.login,
                    "server": acc.server,
                    "account_type": acc.account_type,
                    "currency": acc.currency,
                    "balance": acc.balance,
                    "equity": acc.equity,
                    "is_active": acc.is_active,
                    "last_sync": acc.last_sync.isoformat()
                }
                for acc in mt5_accounts
            ]
        }
    except Exception as e:
        logger.error(f"Failed to get MT5 accounts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MT5 accounts"
        )

# Password reset endpoints
@router.post("/password/reset/email")
async def reset_password_email(email: EmailStr = Body(..., embed=True)):
    """Send password reset email"""
    try:
        response = supabase_auth_service.client.auth.reset_password_email(email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send password reset email"
        )

@router.post("/password/reset/phone")
async def reset_password_phone(phone: str = Body(..., embed=True)):
    """Send password reset OTP to phone"""
    try:
        response = supabase_auth_service.client.auth.reset_password_phone(phone)
        return {"message": "Password reset OTP sent to phone"}
    except Exception as e:
        logger.error(f"Phone password reset failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send password reset OTP"
        )

# Health check
@router.get("/health")
async def auth_health_check():
    """Authentication service health check"""
    try:
        response = supabase_auth_service.admin_client.table("user_profiles").select("count", count="exact").execute()
        return {
            "status": "healthy",
            "supabase_connected": True,
            "total_users": response.count if hasattr(response, 'count') else 0,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Auth health check failed: {e}")
        return {
            "status": "unhealthy",
            "supabase_connected": False,
            "error": str(e),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

# Admin endpoints (require admin role)
@router.get("/admin/users")
async def get_all_users(
    current_user: UserProfile = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all users (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        result = supabase_auth_service.admin_client.table("user_profiles").select("*").range(skip, skip + limit - 1).execute()
        return {
            "users": result.data,
            "total": len(result.data)
        }
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.put("/admin/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str = Body(..., embed=True),
    current_user: UserProfile = Depends(get_current_user)
):
    """Update user role (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if role not in ["user", "premium", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role"
        )
    
    try:
        result = supabase_auth_service.admin_client.table("user_profiles").update({
            "role": role
        }).eq("id", user_id).execute()
        
        return {"message": f"User role updated to {role}"}
    except Exception as e:
        logger.error(f"Failed to update user role: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        ) 