"""Placeholder removed migration.

Alembic revision 0004_migrate_event_images now performs the migration and is
idempotent. This file is retained as a harmless no-op placeholder to avoid
accidental re-execution.
"""


def main():
    print(
        "This repository no longer requires `scripts/migrate_event_images.py`"
        " — use Alembic migration 0004 instead."
    )


if __name__ == "__main__":
    main()
