from sqlalchemy import Column, String, Integer

from app.infrastructure.postgres_database import Base


class RoverModel(Base):
    __tablename__ = "rovers"

    id = Column(String(36), primary_key=True)
    x = Column(Integer, nullable=False, default=0)
    y = Column(Integer, nullable=False, default=0)
    direction = Column(String(10), nullable=False, default="NORTH")
    plateau_max_x = Column(Integer, nullable=False)
    plateau_max_y = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<RoverModel(id={self.id}, x={self.x}, y={self.y}, direction={self.direction})>"

