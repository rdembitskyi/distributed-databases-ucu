import logging

from db_queries.concurrent_update import (
    atomic_increment_query,
    optimistic_locking_query,
    perform_concurrent_update,
    read_update_write_query,
    select_for_update_query,
)
from db_queries.shared import get_db_connection, set_transaction_isolation_level
from migrations.create_user_count import run_migration


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)-10s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    run_migration()

    clients_amount = 10
    iterations_per_client = 10_000

    conn = get_db_connection()
    set_transaction_isolation_level(conn=conn, use_serializable=False)
    conn.close()

    # Test 1: Lost Updates
    perform_concurrent_update(
        clients_amount=clients_amount,
        query_func=read_update_write_query,
        query_name="Lost Updates",
        iterations_per_client=iterations_per_client,
        enable_retry=False,
    )

    conn = get_db_connection()
    set_transaction_isolation_level(conn=conn, use_serializable=True)
    conn.close()

    # Test 2: Lost Updates with serializable isolation level
    perform_concurrent_update(
        clients_amount=clients_amount,
        query_func=read_update_write_query,
        query_name="Lost Updates",
        iterations_per_client=iterations_per_client,
        enable_retry=True,
    )

    conn = get_db_connection()
    set_transaction_isolation_level(conn=conn, use_serializable=False)
    conn.close()

    # Test 3: In Place update
    perform_concurrent_update(
        clients_amount=clients_amount,
        query_func=atomic_increment_query,
        query_name="In Place update",
        iterations_per_client=iterations_per_client,
        enable_retry=False,
    )

    # Test 4: SELECT FOR UPDATE (row-level locking)
    perform_concurrent_update(
        clients_amount=clients_amount,
        query_func=select_for_update_query,
        query_name="SELECT FOR UPDATE",
        iterations_per_client=iterations_per_client,
        enable_retry=False,
    )

    # Test 5: Optimistic Concurrency Control (version-based)
    perform_concurrent_update(
        clients_amount=clients_amount,
        query_func=optimistic_locking_query,
        query_name="Optimistic Locking (Version)",
        iterations_per_client=iterations_per_client,
        enable_retry=False,
    )
