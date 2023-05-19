from fastapi import FastAPI

from server.config.factory import settings
from server.models.managers import create_db_and_tables, pool_database_clients

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("Starting up...")

    print("Creating relational database and tables...")
    create_db_and_tables()
    print("Relational database and tables created!")

    print("Pooling NoSQL database connections...")
    await pool_database_clients()
    print("NoSQL database connections pooled!")

    print("Startup complete!")


@app.get("/health")
async def health():
    return {"status": "ok", "app_name": settings.APP_NAME}
