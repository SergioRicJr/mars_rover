import abc
from contextlib import contextmanager


class IDatabase(metaclass=abc.ABCMeta):
    """Abstract interface for database operations."""

    @abc.abstractmethod
    def create_database(self) -> None:
        """Creates the database schema."""
        raise NotImplementedError

    @abc.abstractmethod
    def close(self) -> None:
        """Closes the database connection."""
        raise NotImplementedError

    @abc.abstractmethod
    @contextmanager
    def session(self):
        """Provides a database session."""
        raise NotImplementedError
