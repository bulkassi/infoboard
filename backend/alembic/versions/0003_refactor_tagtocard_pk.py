"""Refactor TagToCard to use composite PK

Revision ID: 0003_refactor_tagtocard_pk
Revises: 0002_move_position_fields
Create Date: 2026-05-06 13:00:00.000000

This migration refactors the TagToCard table to use a composite primary key
(card_id, tag_id) instead of a separate id column. It also removes the
card_type column if it exists (no longer needed as tags are CardCommon-only).
"""
from alembic import op
import sqlalchemy as sa


revision = "0003_refactor_tagtocard_pk"
down_revision = "0002_move_position_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Refactor TagToCard to composite PK and remove card_type."""
    # Drop the existing constraint on tagtocard if it has an id PK
    op.drop_constraint("tagtocard_pkey", "tagtocard", type_="primary")
    
    # Remove the id column if it exists
    try:
        op.drop_column("tagtocard", "id")
    except Exception:
        # Column may not exist in all environments
        pass
    
    # Remove card_type column if it exists (not needed with new schema)
    try:
        op.drop_column("tagtocard", "card_type")
    except Exception:
        # Column may not exist in all environments
        pass
    
    # Create new composite primary key on (card_id, tag_id)
    op.create_primary_key(
        "tagtocard_pkey",
        "tagtocard",
        ["card_id", "tag_id"]
    )


def downgrade() -> None:
    """Reverse the TagToCard refactoring."""
    # Drop the composite PK
    op.drop_constraint("tagtocard_pkey", "tagtocard", type_="primary")
    
    # Re-add the id column
    op.add_column(
        "tagtocard",
        sa.Column("id", sa.Integer(), nullable=False, autoincrement=True)
    )
    
    # Create the single id PK
    op.create_primary_key(
        "tagtocard_pkey",
        "tagtocard",
        ["id"]
    )
    
    # Re-add card_type if needed for rollback compatibility
    op.add_column(
        "tagtocard",
        sa.Column("card_type", sa.String(), nullable=True)
    )
