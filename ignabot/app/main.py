from fastapi import FastAPI
from app.routes.bot import router as bot_router

def create_app() -> FastAPI:
    application = FastAPI()
    
    return application


app = create_app()
app.include_router(bot_router)


@app.on_event("startup")
async def startup_event():
    pass

@app.on_event("shutdown")
async def shutdown_event():
    pass