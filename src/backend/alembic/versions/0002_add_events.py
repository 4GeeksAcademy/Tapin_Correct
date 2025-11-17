"""add events table

Revision ID: 0002_add_events
Revises: 0001_initial
Create Date: 2025-11-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_add_events"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "event",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("date_start", sa.DateTime(), nullable=True),
        sa.Column("location_address", sa.Text(), nullable=True),
        sa.Column("location_city", sa.String(length=120), nullable=True),
        sa.Column("location_state", sa.String(length=10), nullable=True),
        sa.Column("location_zip", sa.String(length=20), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("geohash_4", sa.String(length=8), nullable=True),
        sa.Column("geohash_6", sa.String(length=12), nullable=True, index=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("image_urls", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("scraped_at", sa.DateTime(), nullable=True),
        sa.Column("cache_expires_at", sa.DateTime(), nullable=True, index=True),
    )
    op.create_index("ix_event_geohash_6", "event", ["geohash_6"])
    op.create_index("ix_event_cache_expires", "event", ["cache_expires_at"])


def downgrade():
    op.drop_index("ix_event_cache_expires", table_name="event")
    op.drop_index("ix_event_geohash_6", table_name="event")
    op.drop_table("event")
