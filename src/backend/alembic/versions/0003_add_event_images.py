"""add event_image table

Revision ID: 0003_add_event_images
Revises: 0002_add_events
Create Date: 2025-11-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_add_event_images"
down_revision = "0002_add_events"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "event_image",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["event_id"],
            ["event.id"],
        ),
    )
    op.create_index("ix_event_image_event_id", "event_image", ["event_id"])


def downgrade():
    op.drop_index("ix_event_image_event_id", table_name="event_image")
    op.drop_table("event_image")
