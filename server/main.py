from fastapi import FastAPI

from server.config.factory import settings
from server.models.managers import create_db_and_tables

app = FastAPI()


@app.on_event("startup")
def on_startup():
    print("Starting up...")
    create_db_and_tables()
    print("Startup complete!")


@app.get("/health")
async def health():
    return {"status": "ok", "app_name": settings.APP_NAME}
