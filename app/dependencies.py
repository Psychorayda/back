import logging
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

from schemas import TokenDataSchema
from settings import ALGORITHM, SECRET_KEY


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
        self.token_jwt_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not decode JWT",
            headers={"WWW-Authenticate": "Bearer"},
        )   
        
    async def __call__(self, token: str = Depends(oauth2_scheme)) -> TokenDataSchema:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            user_id: int = payload.get("id")
            return TokenDataSchema(user_id=user_id)
        except JWTError:
            logging.warning("JWT decode error")
            raise self.token_jwt_exception
        

class RequestRateLimiter(RateLimited):
    def __init__(self, rate: str, prefix: str = DEFAULT_PREFIX, request_identifier_factory: Optional[RequestIdentifierFactoryType] = None, group: Optional[str] = None):
        super().__init__(BucketingRateLimitStrategy(rate=rate, prefix=prefix, request_identifier_factory=request_identifier_factory, group=group))

    async def __call__(self,  
                       request: Request,
                       redis: Redis = Depends(RedisDependencyMarker),
                    #    token_data: TokenDataSchema = Depends(TokenChecker())
                       ) -> RateLimitStatus:
        ratelimit_status = await super().__call__(request=request, redis=redis)
        return ratelimit_status
    

class PermissionChecker:
    def __init__(self, perm_needed: str = None):
        self.perm_needed = perm_needed
        self.forbidden_exception = HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to do that!"
        )

    async def __call__(self):
        if self.perm_needed is not None:
            raise self.forbidden_exception
        return
