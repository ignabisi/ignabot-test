import json
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
    async def handle_body(self, request):
        """
        Handles the request body by decoding it based on the content type.
        If the request content type is 'multipart/form-data', the request is discarded, assuming
        that the body content is being stored as an Artifact.

        Args:
            request (starlette.responses.StreamingResponse): The incoming request object.

        Returns:
            Union[Dict[str, Any], str]: The decoded request body as a dictionary (if content type is JSON)
                or a string (if content type is not JSON) or a message indicating binary data.
        """
        body = await request.body()
        try:
            body = body.decode("utf-8")
            _body = json.loads(body)
        except json.JSONDecodeError:
            _body = body
        logging.debug(_body)    
        return _body
        
    async def dispatch(self, request: Request, call_next):
        # await self.handle_body(request)
        return await call_next(request)

def create_app() -> FastAPI:
    application = FastAPI()
    # application.add_middleware(TrustHeadersMiddleware)
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