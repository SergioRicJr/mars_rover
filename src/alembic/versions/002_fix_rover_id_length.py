"""Fix rover id column length for UUID

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Altera o tamanho da coluna id de 8 para 36 (UUID)
    op.alter_column('rovers', 'id',
                    existing_type=sa.String(length=8),
                    type_=sa.String(length=36),
                    existing_nullable=False)


def downgrade() -> None:
    op.alter_column('rovers', 'id',
                    existing_type=sa.String(length=36),
                    type_=sa.String(length=8),
                    existing_nullable=False)

