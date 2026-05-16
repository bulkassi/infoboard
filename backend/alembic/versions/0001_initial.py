"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2026-05-06 00:00:00.000000
"""
from alembic import op
from sqlmodel import SQLModel

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    # Create all tables from SQLModel metadata
    SQLModel.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    SQLModel.metadata.drop_all(bind=bind)
