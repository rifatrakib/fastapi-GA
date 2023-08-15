import json
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
from server.utils.messages import raise_410_gone


def create_db_and_tables():
    engine = create_engine(settings.RDS_URI_SYNC, echo=True)
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


def read_from_cache(*, key: str):
    try:
        client: Redis = get_redis_client()
        data = json.loads(client.get(key).decode("utf-8"))
        return data
    except AttributeError:
        raise_410_gone(message="Key has expired!")


def pop_from_cache(*, key: str):
    try:
        client: Redis = get_redis_client()
        data = json.loads(client.get(key).decode("utf-8"))
        client.delete(key)
        return data
    except AttributeError:
        raise_410_gone(message="Key has expired!")


def validate_key(*, key: str):
    client: Redis = get_redis_client()
    return client.exists(key)
