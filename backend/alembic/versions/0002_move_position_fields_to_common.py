"""Move position fields from cardbase to cardcommon

Revision ID: 0002_move_position_fields
Revises: 0001_initial
Create Date: 2026-05-06 12:00:00.000000

This migration moves col, row, col_span, row_span columns from the cardbase 
table to the cardcommon table. These fields are only used for CardCommon cards,
not for CardEmployee or CardService cards.
"""
from alembic import op
import sqlalchemy as sa


revision = "0002_move_position_fields"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Move position fields from cardbase to cardcommon."""
    # For PostgreSQL, we need to:
    # 1. Add the columns to cardcommon with defaults
    # 2. Drop the columns from cardbase
    
    op.add_column(
        "cardcommon",
        sa.Column("col", sa.Integer(), server_default="1", nullable=True)
    )
    op.add_column(
        "cardcommon",
        sa.Column("row", sa.Integer(), server_default="1", nullable=True)
    )
    op.add_column(
        "cardcommon",
        sa.Column("col_span", sa.Integer(), server_default="1", nullable=True)
    )
    op.add_column(
        "cardcommon",
        sa.Column("row_span", sa.Integer(), server_default="1", nullable=True)
    )
    
    # Drop columns from cardbase
    op.drop_column("cardbase", "col")
    op.drop_column("cardbase", "row")
    op.drop_column("cardbase", "col_span")
    op.drop_column("cardbase", "row_span")


def downgrade() -> None:
    """Reverse the position fields migration."""
    # Re-add columns to cardbase
    op.add_column(
        "cardbase",
        sa.Column("col", sa.Integer(), server_default="1", nullable=True)
    )
    op.add_column(
        "cardbase",
        sa.Column("row", sa.Integer(), server_default="1", nullable=True)
    )
    op.add_column(
        "cardbase",
        sa.Column("col_span", sa.Integer(), server_default="1", nullable=True)
    )
    op.add_column(
        "cardbase",
        sa.Column("row_span", sa.Integer(), server_default="1", nullable=True)
    )
    
    # Drop columns from cardcommon
    op.drop_column("cardcommon", "col")
    op.drop_column("cardcommon", "row")
    op.drop_column("cardcommon", "col_span")
    op.drop_column("cardcommon", "row_span")
