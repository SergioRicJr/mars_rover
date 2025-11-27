from typing import Optional
from sqlalchemy import select, update

from app.infrastructure.postgres_database import Base
from app.repositories.irepository import IRepository


class SqlRepository(IRepository):
    model = Base

    def get_all(self):
        with self.session_factory() as session:
            result = session.execute(select(self.model))
            return result.scalars().all()

    def get_by_id(self, id: str) -> Optional[Base]:
        with self.session_factory() as session:
            stmt = select(self.model).where(self.model.id == id)
            result = session.execute(stmt)
            return result.scalar_one_or_none()

    def create(self, values):
        with self.session_factory() as session:
            _model = self.model(**values)
            session.add(_model)
            session.commit()
            return _model

    def update(self, pk, values):
        with self.session_factory() as session:
            session.execute(update(self.model).where(self.model.id == pk).values(**values))
            session.commit()

    def commit(self):
        with self.session_factory() as session:
            session.commit()

    def rollback(self):
        with self.session_factory() as session:
            session.rollback()