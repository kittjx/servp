from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ...db.database import DBSession
from ...models.user import User, WeChatLoginRequest, UserLoginResponse
from typing import Optional, Annotated, List
from datetime import timedelta, datetime, timezone
from jose import JWTError, jwt
import os
import httpx


# Router
auth_router = APIRouter(prefix="/api/v1/auth")


# Configuration
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30 days


# JWT Token data model
from pydantic import BaseModel
class TokenData(BaseModel):
    user_id: int
    openid: str


async def extract_token(request: Request) -> str:
    """Extract JWT token from request header"""
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[len("Bearer "):]
    return token


async def get_current_user_from_token(token: str, session: AsyncSession) -> User:
    """Get current user from JWT token and verify user exists in database"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str: str = payload.get("sub")
        openid: str = payload.get("openid")

        if user_id_str is None or openid is None:
            raise credentials_exception

        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # Check if user exists in database
    statement = select(User).where(User.id == user_id)
    result = await session.exec(statement)
    user = result.one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found in database. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify openid matches (extra security check)
    if user.openid != openid:
        raise credentials_exception

    return user


async def get_current_user(
    token: Annotated[str, Depends(extract_token)],
    session: DBSession
) -> User:
    """Dependency to get current user from Authorization header"""
    return await get_current_user_from_token(token, session)


# Type alias for using in other modules
CurrentUser = Annotated[User, Depends(get_current_user)]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
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
async def get_current_user_endpoint(
    current_user: CurrentUser
):
    """Get current user info"""
    return current_user


def require_leader():
    """Dependency to check if user is a leader"""
    async def role_checker(current_user: CurrentUser) -> User:
        if not current_user.is_leader:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requires leader role"
            )
        return current_user
    return role_checker


def require_admin():
    """Dependency to check if user is an admin"""
    async def role_checker(current_user: CurrentUser) -> User:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requires admin role"
            )
        return current_user
    return role_checker


def require_leader_or_admin():
    """Dependency to check if user is a leader or admin"""
    async def role_checker(current_user: CurrentUser) -> User:
        if not (current_user.is_leader or current_user.is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Requires leader or admin role"
            )
        return current_user
    return role_checker
