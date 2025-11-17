"""migrate event image urls into event_image rows

Revision ID: 0004_migrate_event_images
Revises: 0003_add_event_images
Create Date: 2025-11-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
import json
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = "0004_migrate_event_images"
down_revision = "0003_add_event_images"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    # Fetch existing events that have image_urls or image_url
    sel = sa.text("SELECT id, image_urls, image_url FROM event")
    res = conn.execute(sel)
    insert_stmt = sa.text(
        "INSERT INTO event_image (",
        "event_id, url, caption, position, created_at)",
        " VALUES (:event_id, :url, :caption, :position, :created_at)",
    )
    update_event_image_url = sa.text(
        "UPDATE event SET image_url = :image_url WHERE id = :id"
    )

    for row in res:
        event_id = row["id"]
        image_urls_raw = row["image_urls"]
        current_image_url = row["image_url"]
        # Skip events that already have event_image rows (idempotent)
        count_stmt = sa.text(
            "SELECT COUNT(1) as c FROM event_image WHERE event_id = :event_id"
        )
        cres = conn.execute(count_stmt, {"event_id": event_id})
        crow = cres.fetchone()
        if crow and crow["c"] and crow["c"] > 0:
            continue
        try:
            images = []
            if image_urls_raw:
                # image_urls may be JSON array or a comma-separated string
                try:
                    parsed = json.loads(image_urls_raw)
                    if isinstance(parsed, list):
                        images = [str(i) for i in parsed if i]
                    elif isinstance(parsed, str):
                        images = [parsed]
                except Exception:
                    # fallback: split on commas
                    raw_list = str(image_urls_raw).split(",")
                    raw_parts = [p.strip() for p in raw_list]
                    images = [p for p in raw_parts if p]

            # Insert image rows preserving order
            for idx, url in enumerate(images):
                conn.execute(
                    insert_stmt,
                    {
                        "event_id": event_id,
                        "url": url,
                        "caption": None,
                        "position": idx,
                        "created_at": datetime.now(timezone.utc),
                    },
                )

            # If no thumbnail is set, use the first image (backcompat)
            if (not current_image_url) and images:
                conn.execute(
                    update_event_image_url,
                    {"image_url": images[0], "id": event_id},
                )

        except Exception:
            # Non-fatal for individual rows; continue with others
            continue


def downgrade():
    # Destructive downgrade: remove all migrated event_image rows.
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM event_image"))
