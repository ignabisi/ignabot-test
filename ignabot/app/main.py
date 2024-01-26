import logging
import sys
import traceback

from app.routes.telegram import router as telegram_router
from app.utils import create_db_schemas, create_tables, get_sqlmodel_engine
from fastapi import FastAPI, Request
from sqlmodel import Session
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


class TrustHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        scheme = request.headers.get('x-forwarded-proto')
        if scheme:
            request.scope['scheme'] = scheme
        return await call_next(request)

def create_app() -> FastAPI:
    application = FastAPI()
    application.add_middleware(TrustHeadersMiddleware)
    return application


app = create_app()
app.include_router(telegram_router)


@app.on_event("startup")
async def startup_event():
    try:
        engine = get_sqlmodel_engine()
        
        with Session(engine) as session:
            create_db_schemas(session)
            create_tables(engine)
            
    except Exception as err:
        error_traceback = traceback.format_exception(*sys.exc_info())
        
        error_msg = [
            line.replace("\n", "").replace("^", "").strip() for line in error_traceback
        ]
        
        error_type = type(err).__name__
        response_data = {
            "error_type": error_type,
            "traceback": error_msg,
        }

        logging.error(response_data)

@app.on_event("shutdown")
async def shutdown_event():
    # TODO
    # Add event for shutdown process
    pass