from dependency_injector import containers, providers

from app.config import Config
from app.infrastructure.logger import Logger
from app.infrastructure.postgres_database import PostgresDatabase
from app.repositories.rover_repository import RoverRepository
from app.services.rover_service import RoverService


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        modules=["app.endpoints.rover.controllers"]
    )

    # Logger singleton
    logger = providers.Singleton(Logger)

    # PostgresDatabase singleton
    postgres_database = providers.Singleton(
        PostgresDatabase,
        db_url=Config.DATABASE_URL,
        logger=logger,
        echo=Config.SQL_ECHO,
        pool_size=Config.SQL_POOL_SIZE,
        max_overflow=Config.SQL_MAX_OVERFLOW,
    )

    rover_repository = providers.Singleton(
        RoverRepository,
        session_factory=postgres_database.provided.session,
        logger=logger
    )

    rover_service = providers.Factory(
        RoverService,
        rover_repository=rover_repository,
        logger=logger
    )
