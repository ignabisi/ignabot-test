import sys
import logging 

from fastapi import FastAPI
from sqlmodel import Session

from app.routes.telegram import router as telegram_router
from app.utils import get_sqlmodel_engine, create_db_schemas,create_tables

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def create_app() -> FastAPI:
    application = FastAPI()
    
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
        logging.info(f"Error while connecting to database {repr(err)}")
    pass

@app.on_event("shutdown")
async def shutdown_event():
    # TODO
    # Add event for shutdown process
    pass