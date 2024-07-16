from fastapi import APIRouter, Depends, HTTPException

from dependencies import *


router = APIRouter()

@router.post("/1")
async def test_1(
    ratelimit_status: RateLimitStatus = Depends(RequestRateLimiter(rate="1/5s", group="test"))
):
    print("test_1")
    return ratelimit_status

@router.post("/2")
async def test_2(
    ratelimit_status: RateLimitStatus = Depends(RequestRateLimiter(rate="1/5s", group="test"))
):
    print("test_2")
    return ratelimit_status