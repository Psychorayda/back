from typing import Any
from fastapi import APIRouter, Depends, HTTPException
import aiohttp
from fastapi_ratelimiter.types import RateLimitStatus

from dependencies import RequestRateLimiter
from schemas import TelesSetSchema, TelesCmdSchema


router = APIRouter()

@router.post("/set", 
            summary="set peer's property")
async def setPeerProp(
        teles_set_info: TelesSetSchema,
        ratelimit_status: RateLimitStatus = Depends(RequestRateLimiter(rate="1/5s", group="teles"))
):
    async with aiohttp.ClientSession("http://localhost:18888") as session:
        body = {
            "peer_name": teles_set_info.peer_name,
            "prop_name": teles_set_info.prop_name,
            "val": teles_set_info.val
        }
        async with session.post('/teles/set', json=body) as resp:
            if resp.ok:
                return ratelimit_status
            else:
                raise HTTPException(status_code=resp.status, detail=f"Remote control error: {await resp.text()}")


@router.post("/cmd",
            summary="send peer command")
async def sendPeerCmd(
        teles_cmd_info: TelesCmdSchema,
        ratelimit_status: RateLimitStatus = Depends(RequestRateLimiter(rate="1/5s", group="teles"))
):
    async with aiohttp.ClientSession("http://localhost:18888") as session:
        body = {
            "peer_name": teles_cmd_info.peer_name,
            "command": teles_cmd_info.command
        }
        async with session.post('/teles/cmd', json=body) as resp:
            if resp.ok:
                return ratelimit_status
            else:
                raise HTTPException(status_code=resp.status, detail=f"Remote control error: {await resp.text()}")