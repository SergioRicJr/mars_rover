from contextlib import contextmanager

from sqlalchemy import create_engine, orm
from sqlalchemy.orm import DeclarativeBase, Session, scoped_session, sessionmaker

from app.infrastructure.idatabase import IDatabase
from app.infrastructure.logger import Logger


class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass


class PostgresDatabase(IDatabase):
    def __init__(self, db_url: str, logger: Logger, echo: bool = False, 
                 pool_size: int = 5, max_overflow: int = 10) -> None:
        self._engine = create_engine(
            db_url,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        self._session_factory = scoped_session(
            sessionmaker(
                self._engine,
                expire_on_commit=False,
                class_=Session,
            )
        )
        self._logger = logger

    def create_database(self) -> None:
        Base.metadata.create_all(bind=self._engine)

    def close(self) -> None:
        self._engine.dispose()

    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            self._logger.exception("Postgres Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
            self._session_factory.remove()
