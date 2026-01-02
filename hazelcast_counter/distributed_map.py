import logging
from multiprocessing import Process
import time

import hazelcast


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(processName)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


MAP_NAME = "my-distributed-map"
CLUSTER_NAME = "hello-world"
COUNTER_KEY = "counter"


def increment_counter_naive(process_id, iterations):
    """Race condition worker"""
    client = hazelcast.HazelcastClient(
        cluster_name=CLUSTER_NAME,
    )

    distributed_map = client.get_map(MAP_NAME).blocking()
    logger.info(f"Process {process_id} started")

    for i in range(iterations):
        if i % 1000 == 0:
            logger.info(f"Process {process_id} - Iteration {i}")
        current_value = distributed_map.get(COUNTER_KEY)

        distributed_map.put(COUNTER_KEY, current_value + 1)

    logger.info(f"Process {process_id} finished")
    client.shutdown()


def increment_counter_pessimistic_lock(process_id, iterations):
    client = hazelcast.HazelcastClient(
        cluster_name=CLUSTER_NAME,
    )
    distributed_map = client.get_map(MAP_NAME).blocking()
    logger.info(f"Process {process_id} started")

    for i in range(iterations):
        if i % 1000 == 0:
            logger.info(f"Process {process_id} - Iteration {i}")
        try:
            distributed_map.lock(COUNTER_KEY)
            current_value = distributed_map.get(COUNTER_KEY)
            distributed_map.put(COUNTER_KEY, current_value + 1)
        finally:
            distributed_map.unlock(COUNTER_KEY)

    logger.info(f"Process {process_id} finished")
    client.shutdown()


def increment_counter_optimistic_lock(process_id, iterations):
    client = hazelcast.HazelcastClient(
        cluster_name=CLUSTER_NAME,
    )
    distributed_map = client.get_map(MAP_NAME).blocking()
    logger.info(f"Process {process_id} started")

    for i in range(iterations):
        if i % 1000 == 0:
            logger.info(f"Process {process_id} - Iteration {i}")

        while True:
            current_value = distributed_map.get(COUNTER_KEY)
            new_value = current_value + 1
            result = distributed_map.replace_if_same(
                COUNTER_KEY, current_value, new_value
            )
            if result:
                break

    logger.info(f"Process {process_id} finished")
    client.shutdown()


if __name__ == "__main__":
    # Initialize the counter
    client = hazelcast.HazelcastClient(
        cluster_name="hello-world",
    )

    distributed_map = client.get_map(MAP_NAME).blocking()
    distributed_map.put("counter", 0)
    logger.info("Counter initialized to 0")
    client.shutdown()

    # Configuration
    num_processes = 10
    iterations_per_process = 10_000
    expected_total = num_processes * iterations_per_process

    logger.info(
        f"Starting {num_processes} processes, each doing {iterations_per_process} increments"
    )
    logger.info(f"Expected final value: {expected_total}")

    # Create and start processes
    processes = []
    start_time = time.time()

    target_func = increment_counter_optimistic_lock
    for process_id in range(num_processes):
        p = Process(target=target_func, args=(process_id, iterations_per_process))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()

    end_time = time.time()

    # Check final value
    client = hazelcast.HazelcastClient(
        cluster_name=CLUSTER_NAME,
    )
    distributed_map = client.get_map(MAP_NAME).blocking()
    final_value = distributed_map.get(COUNTER_KEY)

    logger.info("=" * 50)
    logger.info(f"All processes completed in {end_time - start_time:.2f} seconds")
    logger.info(f"Expected value: {expected_total}")
    logger.info(f"Actual value:   {final_value}")
    logger.info(f"Lost updates:   {expected_total - final_value}")
    logger.info("=" * 50)

    client.shutdown()
