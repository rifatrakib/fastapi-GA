from sqlmodel import create_engine

from server.models.schemas.users import BaseSQLTable as UserTables


def create_db_and_tables():
    engine = create_engine("sqlite:///database.db", echo=True, connect_args={"check_same_thread": False})
    UserTables.metadata.create_all(engine)
