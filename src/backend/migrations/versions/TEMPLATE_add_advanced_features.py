"""Add ML, gamification, and admin features

Revision ID: TEMPLATE_ADD_ADVANCED_FEATURES
Revises: <previous_revision>
Create Date: 2025-11-26

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "TEMPLATE_ADD_ADVANCED_FEATURES"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Taste profiles
    op.create_table(
        "taste_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("category_preferences", sa.JSON(), nullable=True),
        sa.Column("location_preferences", sa.JSON(), nullable=True),
        sa.Column("time_preferences", sa.JSON(), nullable=True),
        sa.Column("adventure_level", sa.Float(), nullable=True),
        sa.Column("social_preference", sa.Float(), nullable=True),
        sa.Column("commitment_level", sa.Float(), nullable=True),
        sa.Column("price_sensitivity", sa.String(length=20), nullable=True),
        sa.Column("model_version", sa.String(length=20), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteer_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("volunteer_id"),
    )

    # Achievements
    op.create_table(
        "achievements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon_url", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.Column("criteria", sa.JSON(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # User achievements
    op.create_table(
        "user_achievements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("achievement_id", sa.Integer(), nullable=False),
        sa.Column("unlocked_at", sa.DateTime(), nullable=True),
        sa.Column("progress", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["achievement_id"], ["achievements.id"]),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteer_profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "volunteer_id", "achievement_id", name="unique_user_achievement"
        ),
    )


def downgrade():
    op.drop_table("user_achievements")
    op.drop_table("achievements")
    op.drop_table("taste_profiles")
