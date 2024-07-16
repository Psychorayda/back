import signal
import sys
import time
import uuid
import aioredis
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from fastapi_ratelimiter import RedisDependencyMarker

from models import BaseModel, RequestLogModel
from database import engine, get_session
from apis.base import api_list
from settings import req_id_ctx

from logger import system_logger
from apis.websocket import manager


app = FastAPI()

redis = aioredis.from_url("redis://localhost")
app.dependency_overrides[RedisDependencyMarker] = lambda: redis

for api in api_list:
    app.include_router(api["router"], prefix=api["prefix"], tags=api["tags"], dependencies=api["dependencies"])

app.add_middleware(
            CORSMiddleware,
            allow_origins = ["*"],
            allow_credentials = True,
            allow_methods = ["*"],
            allow_headers = ["*"]
        )

@app.middleware("http")
async def recordProcessTime(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def recordRequestLog(request: Request, call_next):
    req_id = str(uuid.uuid4())
    req_id_ctx.set(req_id)
    response: Response = await call_next(request)
    # session = get_session()
    # try:
    #     request_log = RequestLogModel(
    #         #TODO: frontend should include customized headers {user, role} when request
    #         user = request.headers.get("user"),
    #         role = request.headers.get("role"),
    #         host = request.client.host,
    #         method = request.method,
    #         url = request.url,
    #         path_params = ', '.join([f'{key}: {value}' for key, value in request.path_params.items()]) if request.path_params else None,
    #         query_params= ', '.join([f'{key}: {value}' for key, value in request.query_params.items()]) if request.query_params else None,
    #         response_status = response.status_code,
    #         content_length = response.headers["content-length"],
    #         process_time = response.headers["X-Process-Time"],
    #         req_id = req_id
    #     )
    #     session.add(request_log)
    #     session.commit()
    # except Exception as error_info:
    #     session.rollback()
    #     print(f"Failed to write request log to database by error {error_info}")
    # finally:
    #     session.close()
    req_id_ctx.set(None)
    return response

@app.middleware("http")
async def db_session(request: Request, call_next):
    request.state.db_session = get_session()
    response: Response = await call_next(request)
    request.state.db_session.close()
    return response


@app.on_event("startup")
def startup_event():
    BaseModel.metadata.create_all(bind=engine, checkfirst=True)

@app.on_event("shutdown")
def shutdown_event():
    pass

def handle_shutdown(signum, frame):
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    import uvicorn
    uvicorn.run("main:app", port=9090, reload=True)