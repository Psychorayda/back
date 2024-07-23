import asyncio
import aiohttp
from aiohttp import web
from typing import List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
# from fastapi.websockets import WebSocketState

from logger import system_logger


# class Connection:
#     _counter = 0  # Class variable to track instance count

#     def __init__(self, ws1: Optional[WebSocket] = None, ws2: Optional[aiohttp.ClientWebSocketResponse] = None, forward_task: Optional[asyncio.Task] = None) -> None:
#         Connection._counter += 1
#         self.id = Connection._counter
#         self.ws1 = ws1
#         self.ws2 = ws2
#         self.forward_task = forward_task

#     async def forward_websocket(self, ws1_ready_fut: asyncio.Future, ws2_ready_fut: asyncio.Future):
#         try:
#             ws2_url = "ws://localhost:18888/ws/"
#             async with aiohttp.ClientSession() as session:
#                 async with session.ws_connect(ws2_url) as self.ws2:
#                     ws2_ready_fut.set_result(self.ws2)
#                     await ws1_ready_fut
#                     try:
#                         async for msg in self.ws2:
#                             await self.ws1.send_text(data=msg.data)
#                     except Exception as e:
#                         system_logger.error(f"{self.id}: Error sending message to WS1: {e}")
#         except asyncio.CancelledError:
#             system_logger.warning(f"{self.id}: WS2 forwarding cancelled")
#             await self.ws2.close()
#             raise
#         except Exception as e:
#             system_logger.error(f"{self.id}: WS2 connection error: {e}")
#             ws2_ready_fut.set_exception(e)
#             raise
#         finally:
#             system_logger.info(f"{self.id}: WS2 End")

# class WebSocketManager:
#     def __init__(self):
#         self.active_connections: List[Connection] = []

#     async def connect(self, ws1: WebSocket):
#         conn = Connection(ws1=ws1)
#         ws1_ready_fut = asyncio.Future()
#         try:
#             ws2_ready_fut = asyncio.Future()
#             forward_task = asyncio.create_task(conn.forward_websocket(ws1_ready_fut, ws2_ready_fut))
#             ws2: aiohttp.ClientWebSocketResponse = await ws2_ready_fut
#             await ws1.accept()
#             ws1_ready_fut.set_result(ws1)
#             conn.forward_task = forward_task
#             self.active_connections.append(conn)
#             system_logger.info(f"{conn.id}: Connection constructed")
#         except Exception as e:
#             system_logger.error(f"Error during connection: {e}")
#             raise

#     async def send_message_remote(self, message: str, websocket: WebSocket):
#         for conn in self.active_connections:
#             if conn.ws1 == websocket:
#                 try:
#                     await conn.ws2.send_str(message)
#                 except Exception as e:
#                     system_logger.error(f"{conn.id}: Error sending message to WS2: {e}")
#                     await conn.ws1.close()

#     async def front_disconnect(self, websocket: WebSocket):
#         for conn in self.active_connections:
#             if conn.ws1 == websocket:
#                 conn.forward_task.cancel()
#                 try:
#                     await conn.forward_task
#                 except asyncio.CancelledError:
#                     self.active_connections.remove(conn)
#                     system_logger.warning(f"{conn.id}: WS1 end")

#     async def broadcast(self, message: str):
#         for conn in self.active_connections:
#             await conn.ws1.send_text(message)

# manager = WebSocketManager()
# router = APIRouter()

# @router.websocket("/")
# async def websocket_endpoint(websocket: WebSocket):
#     try: 
#         await manager.connect(websocket)
#     except Exception as e:
#         system_logger.error(f"Error during websocket connect: {e}")
#     else:
#         try:
#             while True:
#                 message = await websocket.receive_text()
#                 await manager.send_message_remote(message, websocket)
#         except WebSocketDisconnect:
#             await manager.front_disconnect(websocket)
#         except Exception as e:
#             system_logger.error(f"Error during message handling: {e}")


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
        # self.front_forward_remote: Optional[asyncio.Task] = None
        # self.remote_forward_front: Optional[asyncio.Task] = None


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[Connection] = []

    async def connect(self, websocket: WebSocket):
        conn = Connection()
        try:
            # task1 = asyncio.create_task(self.front_forward_remote(conn))
            # task2 = asyncio.create_task(self.remote_forward_front(conn))
            await self.connect_remote(conn=conn)
            await self.connect_front(websocket_front=websocket, conn=conn)
            # conn.front_forward_remote = task1
            # conn.remote_forward_front = task2
            self.active_connections.append(conn)
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
                        await conn.ws2.send_str(data=message)
                except Exception as e:
                    system_logger.error(f"Error during send message to remote: {e}")
                    raise

    async def remote_forward_front(self, conn: Connection):
        await conn.ws1_ready_fut
        await conn.ws2_ready_fut
        try:
            async for msg in conn.ws2:
                await conn.ws1.send_text(data=msg.data)            
        except Exception as e:
            system_logger.error(f"Error during send message to front: {e}")
            raise
    
    async def connect_front(self, websocket_front: WebSocket, conn: Connection):
        try:
            await websocket_front.accept()
            conn.ws1 = websocket_front
            conn.ws1_ready_fut.set_result(websocket_front)
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
        except Exception as e:
            system_logger.error(f"Error during construct websocket to remote: {e}")
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
            pass

