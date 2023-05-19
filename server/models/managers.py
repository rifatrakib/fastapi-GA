from sqlmodel import create_engine

from server.config.factory import settings
from server.models.schemas.users import BaseSQLTable as UserTables


def create_db_and_tables():
    if "sqlite" in settings.RDS_URI:
        connect_args = {"check_same_thread": False}
        engine = create_engine(settings.RDS_URI, echo=True, connect_args=connect_args)
    else:
        engine = create_engine(settings.RDS_URI, echo=True)

    UserTables.metadata.create_all(engine)
