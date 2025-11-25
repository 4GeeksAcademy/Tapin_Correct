"""add values columns to listing and event

Revision ID: 0004_add_values_columns
Revises: 0003_add_event_images
Create Date: 2025-11-24 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_add_values_columns"
down_revision = "0003_add_event_images"
branch_labels = None
depends_on = None


def upgrade():
    # Add values column to listing table
    op.add_column("listing", sa.Column("values", sa.Text(), nullable=True))

    # Add values column to event table
    op.add_column("event", sa.Column("values", sa.Text(), nullable=True))


def downgrade():
    # Remove values column from event table
    op.drop_column("event", "values")

    # Remove values column from listing table
    op.drop_column("listing", "values")
