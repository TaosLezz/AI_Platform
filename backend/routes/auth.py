from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_db
from models.database import User, UserRole, UsageLimit, ROLE_LIMITS
from auth.security import AuthService, get_current_active_user
from auth.oauth import oauth, get_google_user_info, get_github_user_info

router = APIRouter()

# Pydantic models for requests/responses
class UserRegister(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: UserRole
    is_active: bool
    email_verified: bool
    avatar_url: Optional[str]
    bio: Optional[str]
    company: Optional[str]
    location: Optional[str]
    website: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None

def create_user_usage_limits(db: Session, user_id: int, role: UserRole):
    """Create usage limits for new user based on role"""
    limits = ROLE_LIMITS[role]
    usage_limit = UsageLimit(
        user_id=user_id,
        daily_generate_limit=limits["daily_generate"],
        daily_classify_limit=limits["daily_classify"],
        daily_detect_limit=limits["daily_detect"],
        daily_segment_limit=limits["daily_segment"],
        daily_chat_limit=limits["daily_chat"],
        monthly_generate_limit=limits["monthly_generate"],
        monthly_classify_limit=limits["monthly_classify"],
        monthly_detect_limit=limits["monthly_detect"],
        monthly_segment_limit=limits["monthly_segment"],
        monthly_chat_limit=limits["monthly_chat"],
    )
    db.add(usage_limit)
    db.commit()
    return usage_limit

@router.post("/register", response_model=TokenResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with email and password"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=UserRole.FREE,
        is_active=True,
        email_verified=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create usage limits
    create_user_usage_limits(db, new_user.id, new_user.role)
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": str(new_user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(new_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(**new_user.__dict__)
    )

@router.post("/login", response_model=TokenResponse)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user with email and password"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not AuthService.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse(**user.__dict__)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserResponse(**current_user.__dict__)

@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(**current_user.__dict__)

@router.get("/google")
async def google_auth(request: Request):
    """Initiate Google OAuth login"""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await get_google_user_info(request, token)
        
        # Check if user exists
        user = db.query(User).filter(
            (User.google_id == user_info['google_id']) | 
            (User.email == user_info['email'])
        ).first()
        
        if user:
            # Update existing user
            user.google_id = user_info['google_id']
            user.avatar_url = user_info.get('avatar_url')
            user.email_verified = user_info.get('email_verified', False)
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                email=user_info['email'],
                username=user_info['email'].split('@')[0],  # Generate username from email
                full_name=user_info.get('full_name'),
                google_id=user_info['google_id'],
                avatar_url=user_info.get('avatar_url'),
                role=UserRole.FREE,
                is_active=True,
                email_verified=user_info.get('email_verified', False)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create usage limits
            create_user_usage_limits(db, user.id, user.role)
        
        db.commit()
        
        # Create tokens
        access_token = AuthService.create_access_token(data={"sub": str(user.id)})
        refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(**user.__dict__)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Google OAuth failed: {str(e)}")

@router.get("/github")
async def github_auth(request: Request):
    """Initiate GitHub OAuth login"""
    redirect_uri = request.url_for('github_callback')
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    try:
        token = await oauth.github.authorize_access_token(request)
        user_info = await get_github_user_info(request, token)
        
        # Check if user exists
        user = db.query(User).filter(
            (User.github_id == user_info['github_id']) | 
            (User.email == user_info['email'])
        ).first()
        
        if user:
            # Update existing user
            user.github_id = user_info['github_id']
            user.avatar_url = user_info.get('avatar_url')
            user.bio = user_info.get('bio')
            user.company = user_info.get('company')
            user.location = user_info.get('location')
            user.website = user_info.get('website')
            user.email_verified = user_info.get('email_verified', False)
            user.last_login = datetime.utcnow()
        else:
            # Create new user
            user = User(
                email=user_info['email'],
                username=user_info.get('username', user_info['email'].split('@')[0]),
                full_name=user_info.get('full_name'),
                github_id=user_info['github_id'],
                avatar_url=user_info.get('avatar_url'),
                bio=user_info.get('bio'),
                company=user_info.get('company'),
                location=user_info.get('location'),
                website=user_info.get('website'),
                role=UserRole.FREE,
                is_active=True,
                email_verified=user_info.get('email_verified', False)
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create usage limits
            create_user_usage_limits(db, user.id, user.role)
        
        db.commit()
        
        # Create tokens
        access_token = AuthService.create_access_token(data={"sub": str(user.id)})
        refresh_token = AuthService.create_refresh_token(data={"sub": str(user.id)})
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse(**user.__dict__)
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"GitHub OAuth failed: {str(e)}")