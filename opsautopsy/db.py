import os
import psycopg2
from opsautopsy.config import get_db_url


def get_connection():
    db_url = os.getenv("DATABASE_URL") or get_db_url()

    if not db_url:
        raise RuntimeError(
            "Database URL not configured.\n"
            "Run: opsautopsy config set-db <postgres-url>"
        )

    return psycopg2.connect(db_url)
