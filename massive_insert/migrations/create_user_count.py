#!/usr/bin/env python3
import logging
import os

import psycopg


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_migration():
    """Create user_count table if not exists with user_id, count, and version fields"""
    # Database connection parameters
    db_params = {
        "host": os.getenv("DB_HOST", "localhost"),
        "dbname": os.getenv("DB_NAME", "mydb"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", "postgres"),
        "port": int(os.getenv("DB_PORT", 5432)),
    }

    try:
        logger.info(
            "Connecting to PostgreSQL at %s:%s", db_params["host"], db_params["port"]
        )
        with psycopg.connect(**db_params) as conn, conn.cursor() as cur:
            logger.info("Creating table user_count if not exists...")

            cur.execute("""
                    CREATE TABLE IF NOT EXISTS user_count (
                        user_id BIGINT PRIMARY KEY,
                        count INTEGER NOT NULL DEFAULT 0,
                        version INTEGER NOT NULL DEFAULT 0
                    );
                """)

            conn.commit()
            logger.info("Table user_count created successfully!")

    except Exception as e:
        logger.error("Error during migration: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    run_migration()
