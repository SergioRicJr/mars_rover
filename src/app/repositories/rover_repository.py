from app.infrastructure.models import RoverModel
from app.repositories.sql_repository import SqlRepository


class RoverRepository(SqlRepository):
    model = RoverModel
