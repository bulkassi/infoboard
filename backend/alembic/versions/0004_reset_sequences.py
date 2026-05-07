"""reset sequences

Revision ID: 0004_reset_sequences
Revises: 0003_refactor_tagtocard_pk
Create Date: 2026-05-07 00:00:00.000000

This migration exists to restore the revision chain expected by the database.
The schema in this repository uses integer identity/serial-like columns, but the
actual sequence reset logic is intentionally kept as a no-op here because the
current model definitions and migrations do not define sequence-managed tables
that require additional data movement.
"""
from alembic import op


revision = "0004_reset_sequences"
down_revision = "0003_refactor_tagtocard_pk"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """No-op placeholder to complete the revision chain."""
    pass


def downgrade() -> None:
    """No-op placeholder for downgrade symmetry."""
    pass
