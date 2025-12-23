"""Initial tables

Revision ID: 3b95f906481d
Revises: 
Create Date: 2025-12-19 11:40:39.414994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = '3b95f906481d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis;')
    
    # Создаем таблицу features
    op.create_table('features',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('geom', geoalchemy2.Geometry(geometry_type='GEOMETRY', srid=4326), nullable=True),
        sa.Column('geom_type', sa.String(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('features')
    # Удаляем расширение PostGIS (осторожно, только если больше не используется)
    op.execute('DROP EXTENSION IF EXISTS postgis CASCADE;')