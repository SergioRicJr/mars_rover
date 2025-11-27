import abc

from app.infrastructure.idatabase import IDatabase
from app.infrastructure.logger import Logger


class IRepository(metaclass=abc.ABCMeta):
    def __init__(self, session_factory: IDatabase.session, logger: Logger) -> None:
        self.session_factory = session_factory
        self.logger = logger