from typing import Sequence, Union, Callable, Optional, Awaitable
from aioredis import Redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import asyncio
from fastapi_ratelimiter.types import RateLimitStatus
from fastapi_ratelimiter import RateLimited, RedisDependencyMarker
from fastapi_ratelimiter.strategies import BucketingRateLimitStrategy
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
DEFAULT_PREFIX = "rl:"
RequestIdentifierFactoryType = Callable[[Request], Union[str, bytes, Awaitable[Union[str, bytes]]]]


class DB_Session:
    def __init__(self, need_db_session: bool = True):
        self.need_db_session = need_db_session

    async def __call__(self, request: Request) -> Session | None:
        if self.need_db_session:
            db_session: Session = request.state.db_session
            return db_session
        else:
            return None


class TokenChecker:
    def __init__(self):
        self.token_user_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token user id is None",
            headers={"WWW-Authenticate": "Bearer"},
        )
        self.token_jwt_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode JWT",
            headers={"WWW-Authenticate": "Bearer"},
        )   
        
    async def __call__(self, token: str = Depends(oauth2_scheme)) -> TokenData:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("user_id")
            user_online = user_manager.getUserByID(id=user_id)
            if user_id is None:
                raise self.token_user_exception
            token_data = TokenData(user_id=user_id, user_online=user_online)
            return token_data
        except JWTError:
            logger.warning("JWT decode error")
            raise self.token_jwt_exception