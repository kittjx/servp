from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...db.database import DBSession
from ...models.user import User, WeChatLoginRequest, UserLoginResponse
from typing import Optional
import httpx
from datetime import timedelta
from jose import JWTError, jwt
import os


# Router
auth_router = APIRouter(prefix="/api/v1/auth")


# Configuration
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_wechat_openid(code: str) -> dict:
    """Exchange WeChat login code for openid and session_key"""
    url = "https://api.weixin.qq.com/sns/jscode2session"
    params = {
        "appid": WECHAT_APP_ID,
        "secret": WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        result = response.json()
    
    if "errcode" in result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"WeChat API error: {result.get('errmsg', 'Unknown error')}"
        )
    
    return result


@auth_router.post("/wechat-login", response_model=UserLoginResponse)
async def wechat_login(request: WeChatLoginRequest, session: DBSession):
    """
    WeChat Mini Program Login
    - code: The code from uni.login()
    - user_info: User profile data (nickname, avatarUrl, etc.)
    """
    # Step 1: Exchange code for openid and session_key
    wechat_data = await get_wechat_openid(request.code)
    openid = wechat_data.get("openid")
    
    if not openid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get openid from WeChat"
        )
    
    # Step 2: Check if user exists
    statement = select(User).where(User.openid == openid)
    result = await session.exec(statement)
    user = result.one_or_none()
    
    # Step 3: Create or update user
    if user:
        # Update user info if provided
        if request.user_info:
            user.nickname = request.user_info.get("nickName", user.nickname)
            user.avatar_url = request.user_info.get("avatarUrl", user.avatar_url)
            user.gender = request.user_info.get("gender", user.gender)
            user.city = request.user_info.get("city", user.city)
            user.province = request.user_info.get("province", user.province)
            user.country = request.user_info.get("country", user.country)
            user.language = request.user_info.get("language", user.language)
            user.updated_at = datetime.utcnow()
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
    else:
        # Create new user
        user_info = request.user_info or {}
        user = User(
            openid=openid,
            nickname=user_info.get("nickName"),
            avatar_url=user_info.get("avatarUrl"),
            gender=user_info.get("gender", 0),
            city=user_info.get("city"),
            province=user_info.get("province"),
            country=user_info.get("country"),
            language=user_info.get("language")
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    
    # Step 4: Generate JWT token
    access_token = create_access_token(
        data={"sub": str(user.id), "openid": user.openid}
    )
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user
    )


@auth_router.get("/me", response_model=User)
async def get_current_user(user_id: int, session: DBSession):
    """Get current user info"""
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    user = result.one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
