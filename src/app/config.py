from os import getenv


class Config:
    LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
    SERVER_PORT = int(getenv("SERVER_PORT", "8000"))

    # Database configuration
    DATABASE_URL = getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/mars_rover"
    )

    # SQLAlchemy configuration
    SQL_ECHO = getenv("SQL_ECHO", "false").lower() == "true"
    SQL_POOL_SIZE = int(getenv("SQL_POOL_SIZE", "5"))
    SQL_MAX_OVERFLOW = int(getenv("SQL_MAX_OVERFLOW", "10"))
