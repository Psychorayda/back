import asyncio
import aiohttp
from aiohttp import web
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from logger import system_logger


class Connection:
    _counter = 0  # Class variable to track instance count

    def __init__(self) -> None:
        Connection._counter += 1
        self.id = Connection._counter
        self.ws1_ready_fut = asyncio.Future()
        self.ws2_ready_fut = asyncio.Future()
        self.ws1: Optional[WebSocket] = None
        self.ws2: Optional[aiohttp.ClientWebSocketResponse] = None
        self.ws2_session: Optional[aiohttp.ClientSession] = None
        self.task: asyncio.Task = None


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[Connection] = []

    async def connect(self, websocket: WebSocket):
        conn = Connection()
        try:
            await self.connect_remote(conn=conn)
            await self.connect_front(websocket_front=websocket, conn=conn)
            # Start the remote to front forwarding after the connections are established
            conn.task = asyncio.create_task(self.remote_forward_front(conn))
            self.active_connections.append(conn)
            system_logger.info(f"Connection: {conn.id} built")
        except Exception as e:
            raise

    async def front_forward_remote(self, websocket: WebSocket):
        for conn in self.active_connections:
            if conn.ws1 == websocket:
                await conn.ws1_ready_fut
                await conn.ws2_ready_fut
                try:    
                    while True:
                        message = await conn.ws1.receive_text()
                        # system_logger.info(f"Message from front: {message}")
                        await conn.ws2.send_str(data=message)
                except Exception as e:
                    system_logger.error(f"Error during send message to remote: {e}")
                    await self.disconnect_front(conn)
                    raise
                finally:
                    await self.disconnect_remote(conn)
                    self.active_connections.remove(conn)
                    

    async def remote_forward_front(self, conn: Connection):
        try:
            await conn.ws1_ready_fut
            await conn.ws2_ready_fut
            try:
                async for msg in conn.ws2:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        # system_logger.info(f"Message from remote: {msg.data}")
                        await conn.ws1.send_text(data=msg.data)
                    elif msg.type == aiohttp.WSMsgType.CLOSED:
                        system_logger.warning(f"Connection to remote: {conn.id} closed")
                        break
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        await self.disconnect_remote(conn)
                        break
            except Exception as e:
                system_logger.error(f"Error during send message to front: {e}")
                await self.disconnect_remote(conn)
                raise
        except asyncio.CancelledError:
            raise
        finally:
            await self.disconnect_front(conn)
            self.active_connections.remove(conn)
    
    async def connect_front(self, websocket_front: WebSocket, conn: Connection):
        try:
            await websocket_front.accept()
            conn.ws1 = websocket_front
            conn.ws1_ready_fut.set_result(websocket_front)
            system_logger.info(f"Connection to front: {conn.id} built")
        except Exception as e:
            system_logger.error(f"Error during construct websocket to front: {e}")
            raise

    async def connect_remote(self, conn: Connection):
        try:
            ws_remote_url = "ws://localhost:18888/ws/"
            session = aiohttp.ClientSession()
            conn.ws2_session = session
            websocket_remote = await session._ws_connect(ws_remote_url)
            conn.ws2 = websocket_remote
            conn.ws2_ready_fut.set_result(websocket_remote)
            system_logger.info(f"Connection to remote: {conn.id} built")
        except Exception as e:
            system_logger.error(f"Error during construct websocket to remote: {e}")
            raise

    async def disconnect_front(self, conn: Connection):
        try:
            await conn.ws1.close()
            system_logger.info(f"Connection to front: {conn.id} closed")
        except Exception as e:
            system_logger.error(f"Error during close websocket to front: {e}")
            raise

    async def disconnect_remote(self, conn: Connection):
        try:
            await conn.ws2.close()
            await conn.ws2_session.close()
            conn.task.cancel()
            try:
                await conn.task
            except asyncio.CancelledError:
                system_logger.info(f"Connection to remote: {conn.id} closed")
        except Exception as e:
            system_logger.error(f"Error during close websocket to remote: {e}")
            raise

manager = WebSocketManager()
router = APIRouter()

@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    try: 
        await manager.connect(websocket)
    except Exception as e:
        system_logger.error(f"Error during construct websocket connection: {e}")
    else:
        try:
            await manager.front_forward_remote(websocket)
        except Exception as e:
            print("Websocket connection end")

