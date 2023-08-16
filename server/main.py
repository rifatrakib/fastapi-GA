from fastapi import FastAPI

from server.config.factory import settings
from server.database.managers import (
    create_db_and_tables,
    ping_redis_server,
    pool_database_clients,
)
from server.routes.auth import router as auth_router
from server.routes.products import router as products_router
from server.routes.shops import router as shops_router
from server.routes.users import router as users_router
from server.schemas.base import HealthResponseSchema

app = FastAPI()
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(products_router)
app.include_router(shops_router)


@app.on_event("startup")
async def on_startup():
    print("Starting up...")

    print("Creating relational database and tables...")
    create_db_and_tables()
    print("Relational database and tables created!")

    print("Pooling NoSQL database connections...")
    await pool_database_clients()
    print("NoSQL database connections pooled!")

    print("Ping Redis server...")
    ping_redis_server()
    print("Redis server pinged!")

    print("Startup complete!")


@app.get("/health", response_model=HealthResponseSchema)
async def health():
    return settings
