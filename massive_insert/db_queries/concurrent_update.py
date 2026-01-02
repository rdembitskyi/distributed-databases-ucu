from collections.abc import Callable
import logging
import threading
import time

from db_queries.shared import get_db_connection
from psycopg import errors


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(threadName)-10s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def read_update_write_query(cursor, user_id: int):
    """Query strategy: SELECT then UPDATE (prone to race conditions)"""
    cursor.execute("SELECT count FROM user_count WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    counter = result[0]
    counter = counter + 1
    cursor.execute(
        "UPDATE user_count SET count = %s WHERE user_id = %s", (counter, user_id)
    )


def atomic_increment_query(cursor, user_id: int):
    """Query strategy: Atomic UPDATE (no race conditions)"""
    cursor.execute(
        "UPDATE user_count SET count = count + 1 WHERE user_id = %s", (user_id,)
    )


def select_for_update_query(cursor, user_id: int):
    """Query strategy: SELECT FOR UPDATE then UPDATE (row-level locking)"""
    cursor.execute(
        "SELECT count FROM user_count WHERE user_id = %s FOR UPDATE", (user_id,)
    )
    result = cursor.fetchone()
    counter = result[0] + 1
    cursor.execute(
        "UPDATE user_count SET count = %s WHERE user_id = %s", (counter, user_id)
    )


def optimistic_locking_query(cursor, user_id: int):
    """Query strategy: Optimistic concurrency control using version field"""
    max_retries = 100  # Prevent infinite loop

    for attempt in range(max_retries):
        # Read current counter and version
        cursor.execute(
            "SELECT count, version FROM user_count WHERE user_id = %s", (user_id,)
        )
        result = cursor.fetchone()
        counter, version = result

        # Increment counter
        counter = counter + 1
        new_version = version + 1

        # Try to update only if version hasn't changed
        cursor.execute(
            "UPDATE user_count SET count = %s, version = %s WHERE user_id = %s AND version = %s",
            (counter, new_version, user_id, version),
        )

        # Check if update succeeded
        if cursor.rowcount > 0:
            break

        # If we get here, someone else updated the row (version changed), retry
        if attempt == max_retries - 1:
            raise Exception(f"Optimistic locking failed after {max_retries} attempts")


def worker(
    worker_id: int,
    iterations: int,
    user_id: int,
    query_func: Callable,
    enable_retry: bool,
):
    """Worker thread that performs concurrent updates using provided query function"""
    logger.info(f"Worker {worker_id} starting with {iterations} iterations")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        for i in range(iterations):
            max_attempts = 10 if enable_retry else 1

            for attempt in range(max_attempts):
                try:
                    query_func(cursor, user_id)
                    conn.commit()
                    break
                except errors.SerializationFailure:
                    conn.rollback()
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Worker {worker_id} serialization failure, retry {attempt + 1}/{max_attempts}"
                        )
                        time.sleep(0.3)  # simple backoff
                        continue

        logger.info(f"Worker {worker_id} finished all {iterations} iterations")

    except Exception as e:
        logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
    finally:
        cursor.close()
        conn.close()


def perform_concurrent_update(
    clients_amount: int,
    query_func: Callable,
    query_name: str,
    iterations_per_client: int = 10_000,
    user_id: int = 1,
    enable_retry: bool = False,
):
    """General wrapper function for concurrent update tests

    Args:
        clients_amount: Number of concurrent clients (threads)
        query_func: Function that performs the update query
        query_name: Name of the query strategy (for logging)
        iterations_per_client: Number of iterations each client performs
        user_id: User ID to update
        enable_retry: Enable retry logic for serialization failures
    """
    expected_final_count = clients_amount * iterations_per_client

    logger.info("=" * 80)
    logger.info(f"Starting concurrent update test: {query_name}")
    logger.info(f"Number of clients: {clients_amount}")
    logger.info(f"Iterations per client: {iterations_per_client}")
    logger.info(f"Expected final count: {expected_final_count}")
    logger.info(f"Retry on serialization failure: {enable_retry}")
    logger.info("=" * 80)

    # Setup initial data
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW transaction_isolation")
    result = cursor.fetchone()
    logger.info(f"Transaction isolation level: {result[0]}")

    try:
        cursor.execute(
            """
            INSERT INTO user_count (user_id, count, version)
            VALUES (%s, 0, 0)
            ON CONFLICT (user_id) DO UPDATE SET count = 0, version = 0
        """,
            (user_id,),
        )
        conn.commit()
        logger.info(
            f"Initial data setup complete: user_id={user_id}, count=0, version=0"
        )
    finally:
        cursor.close()
        conn.close()

    # Create and start worker threads
    threads = []
    start_time = time.time()

    for i in range(clients_amount):
        thread = threading.Thread(
            target=worker,
            args=(i + 1, iterations_per_client, user_id, query_func, enable_retry),
            name=f"Worker-{i + 1}",
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    end_time = time.time()
    elapsed = end_time - start_time

    # Get final count
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT count, version FROM user_count WHERE user_id = %s", (user_id,)
        )
        result = cursor.fetchone()
        final_count, final_version = result
    finally:
        cursor.close()
        conn.close()

    logger.info("=" * 80)
    logger.info(f"Query strategy: {query_name}")
    logger.info(f"Test completed in {elapsed:.2f} seconds")
    logger.info(f"Expected final count: {expected_final_count}")
    logger.info(f"Actual final count: {final_count}")
    logger.info(f"Lost updates: {expected_final_count - final_count}")

    if expected_final_count > 0:
        loss_percentage = (
            (expected_final_count - final_count) / expected_final_count * 100
        )
        logger.info(f"Loss percentage: {loss_percentage:.2f}%")

    logger.info("=" * 80)

    return {
        "expected": expected_final_count,
        "actual": final_count,
        "lost": expected_final_count - final_count,
        "elapsed": elapsed,
        "query_name": query_name,
    }
