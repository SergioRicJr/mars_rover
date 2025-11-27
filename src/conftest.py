"""
Fixture configuration for tests.

The tests use in-memory SQLite for isolation and speed.
"""
import pytest
from contextlib import contextmanager
from dependency_injector import providers
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.pool import StaticPool

from main import create_app
from app.containers import Container
from app.infrastructure.postgres_database import Base
from app.infrastructure.idatabase import IDatabase
from app.infrastructure.logger import Logger
from app.repositories.rover_repository import RoverRepository
# Importar modelos para registrá-los no Base.metadata
from app.infrastructure.models import RoverModel  # noqa: F401


class SQLiteTestDatabase(IDatabase):
    """SQLite database implementation for tests."""
    
    def __init__(self, logger: Logger):
        self._engine = create_engine(
            "sqlite:///:memory:",
            echo=False,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self._session_factory = scoped_session(
            sessionmaker(
                bind=self._engine,
                expire_on_commit=False,
                class_=Session,
            )
        )
        self._logger = logger
        Base.metadata.create_all(bind=self._engine)

    def create_database(self) -> None:
        Base.metadata.create_all(bind=self._engine)

    def close(self) -> None:
        Base.metadata.drop_all(bind=self._engine)
        self._engine.dispose()

    @contextmanager
    def session(self):
        session: Session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            self._logger.exception("SQLite Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
            self._session_factory.remove()


@pytest.fixture(scope="function")
def test_db():
    """
    Creates an in-memory SQLite database per test.
    Tables are created and destroyed for each run.
    """
    test_logger = Logger(name="test_logger")
    db = SQLiteTestDatabase(logger=test_logger)
    
    yield db

    db.close()


@pytest.fixture
def client(test_db):
    """Creates a test client wired to the test database."""
    app = create_app()
    
    test_logger = Logger(name="test_logger")

    app.container = Container()
    app.container.postgres_database.override(providers.Object(test_db))
    app.container.logger.override(providers.Object(test_logger))

    app.container.rover_repository.override(
        providers.Singleton(
            RoverRepository,
            session_factory=test_db.session,
            logger=test_logger,
        )
    )
    
    return TestClient(app)


@pytest.fixture
def container(test_db):
    """Creates a clean container for unit tests."""
    test_logger = Logger(name="test_logger")
    
    container = Container()
    container.postgres_database.override(providers.Object(test_db))
    container.logger.override(providers.Object(test_logger))
    
    container.rover_repository.override(
        providers.Singleton(
            RoverRepository,
            session_factory=test_db.session,
            logger=test_logger,
        )
    )
    
    return container
