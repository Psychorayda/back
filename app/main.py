from contextvars import ContextVar
import signal
import sys
import time
import uuid
from fastapi import Depends, FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from models import BaseModel
from database import engine, get_session

from apis.base import api_list


req_id_ctx = ContextVar("request-id")

app = FastAPI()

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
async def db_session(request: Request, call_next):
    request.state.db_session = get_session()
    response: Response = await call_next(request)
    request.state.db_session.close()
    return response

@app.middleware("http")
async def recordRequestLog(request: Request, call_next):
    req_id_ctx.set(str(uuid.uuid4()))
    response: Response = await call_next(request)
    req_id_ctx.set(None)
    return response

@app.middleware("http")
async def recordProcessTime(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
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