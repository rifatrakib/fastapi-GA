from functools import lru_cache
from typing import Any, List, Union

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import parse_obj_as
from redis import Redis
from sqlmodel import create_engine

from server.config.factory import settings
from server.models.base import MapperSchema
from server.models.schemas.users import BaseSQLTable as UserTables


def create_db_and_tables():
    if "sqlite" in settings.RDS_URI:
        connect_args = {"check_same_thread": False}
        engine = create_engine(settings.RDS_URI, echo=True, connect_args=connect_args)
    else:
        engine = create_engine(settings.RDS_URI, echo=True)

    UserTables.metadata.create_all(engine)


def database_collection_mappers() -> List[MapperSchema]:
    models = [
        {
            "database_name": "marketplace",
            "model_paths": [
                "server.models.documents.products.ProductDocument",
            ],
        },
    ]

    return parse_obj_as(obj=models, type_=List[MapperSchema])


async def pool_database_clients():
    client = AsyncIOMotorClient(settings.MONGO_URI)
    mappers = database_collection_mappers()
    for mapper in mappers:
        await init_beanie(
            database=client[mapper.database_name],
            document_models=mapper.model_paths,
        )


@lru_cache()
def get_redis_client() -> Redis:
    return Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


def ping_redis_server():
    client: Redis = get_redis_client()
    return client.ping()


def cache_data(*, key: str, data: Any, ttl: Union[int, None] = None):
    client: Redis = get_redis_client()
    client.set(key, data, ex=ttl)
