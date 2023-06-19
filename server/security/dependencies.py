from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from server.config.factory import settings


def get_database_session() -> Session:
    engine = create_engine(settings.RDS_URI, echo=True)
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()
