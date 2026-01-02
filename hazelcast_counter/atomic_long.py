import logging
from multiprocessing import Process
import time

from hazelcast import HazelcastClient
from hazelcast.config import Config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(processName)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


MAP_NAME = "my-distributed-map"
CLUSTER_NAME = "hello-world"
COUNTER_KEY = "counter"


def increment_counter_atomic_long(process_id, iterations):
    config = Config()
    config.cluster_name = CLUSTER_NAME
    config.connection_timeout = 10.0
    client = HazelcastClient(config=config)
    logger.info(f"Process {process_id} started")
    atomic_long = client.cp_subsystem.get_atomic_long(COUNTER_KEY)
    for i in range(iterations):
        if i % 1000 == 0:
            logger.info(f"Process {process_id} - Iteration {i}")
        atomic_long.increment_and_get().result()

    logger.info(f"Process {process_id} finished")
    client.shutdown()


if __name__ == "__main__":
    # Configuration
    num_processes = 10
    iterations_per_process = 10_000
    expected_total = num_processes * iterations_per_process

    client = HazelcastClient(
        cluster_name=CLUSTER_NAME,
    )
    atomic_long = client.cp_subsystem.get_atomic_long(COUNTER_KEY)
    atomic_long.set(0).result()
    client.shutdown()

    logger.info(
        f"Starting {num_processes} processes, each doing {iterations_per_process} increments"
    )
    logger.info(f"Expected final value: {expected_total}")

    # Create and start processes
    processes = []
    start_time = time.time()

    target_func = increment_counter_atomic_long
    for process_id in range(num_processes):
        p = Process(target=target_func, args=(process_id, iterations_per_process))
        processes.append(p)
        p.start()

    # Wait for all processes to complete
    for p in processes:
        p.join()

    end_time = time.time()

    # Check final value
    client = HazelcastClient(
        cluster_name=CLUSTER_NAME,
    )
    atomic_long = client.cp_subsystem.get_atomic_long(COUNTER_KEY)
    final_value = atomic_long.get().result()

    logger.info("=" * 50)
    logger.info(f"All processes completed in {end_time - start_time:.2f} seconds")
    logger.info(f"Expected value: {expected_total}")
    logger.info(f"Actual value:   {final_value}")
    logger.info(f"Lost updates:   {expected_total - final_value}")
    logger.info("=" * 50)

    client.shutdown()
