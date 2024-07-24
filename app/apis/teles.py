from typing import Any
from fastapi import APIRouter
import aiohttp

from dependencies import *


router = APIRouter()

@router.put("/set", 
            summary="set peer's property")
async def setPeerProp(
        peer_name: str, 
        prop_name: str, 
        val: Any,
        ratelimit_status: RateLimitStatus = Depends(RequestRateLimiter(rate="10/30s", group="teles"))
):
    print(f"{peer_name} {prop_name} {val}")
    return ratelimit_status
    # async with aiohttp.ClientSession("http://localhost:18888") as session:
    #     body = {
    #         "peer_name": peer_name,
    #         "prop_name": prop_name,
    #         "val": val
    #     }
    #     print(body)
    #     async with session.put('/teles/set', json=body) as resp:
    #         print(resp.url)
    #         print(resp.status)
    #         print(await resp.text())

@router.post("/cmd",
            summary="send peer command")
async def sendPeerCmd(
        peer_name: str, 
        command: str,
        ratelimit_status: RateLimitStatus = Depends(RequestRateLimiter(rate="10/30s", group="teles"))
):
    pass