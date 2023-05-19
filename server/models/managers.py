from typing import List

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import parse_obj_as
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
