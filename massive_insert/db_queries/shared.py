import logging
import os

import psycopg


logger = logging.getLogger(__name__)


def get_db_connection():
    """Create a new database connection"""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        dbname=os.getenv("DB_NAME", "mydb"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        port=int(os.getenv("DB_PORT", 5432)),
    )


def set_transaction_isolation_level(conn, use_serializable: bool = False):
    """Set transaction isolation level to READ COMMITTED (default) or SERIALIZABLE"""
    isolation_level = "'serializable'" if use_serializable else "'read committed'"

    with conn.cursor() as cursor:
        cursor.execute(
            f"ALTER DATABASE mydb SET DEFAULT_TRANSACTION_ISOLATION TO {isolation_level}"
        )
        conn.commit()
        cursor.execute("SHOW default_transaction_isolation")
        result = cursor.fetchone()
        logger.info(f"Current isolation level: {result[0]}")
