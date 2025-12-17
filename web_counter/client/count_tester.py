import asyncio
import logging
import sys

from client.config import Config
from domain.stats import StatsResponse
import httpx


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - client - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)


class CountTester:
    def __init__(self, config: Config):
        self.config = config

    async def send_inc_request(
        self, client: httpx.AsyncClient, client_id: int, request_num: int
    ) -> None:
        endpoint = "/inc"
        url = f"{self.config.server.url}{endpoint}"

        try:
            response = await client.post(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Client {client_id} - Request {request_num} - Failed: {e}")

    async def client_worker(self, client_id: int, requests_per_client: int) -> None:
        """Worker coroutine that sends requests sequentially."""
        async with httpx.AsyncClient() as client:
            logger.info(
                f"Client {client_id} starting - will send {requests_per_client} requests"
            )

            for request_num in range(requests_per_client):
                await self.send_inc_request(client, client_id, request_num)

            logger.info(f"Client {client_id} completed")

    async def run(self) -> None:
        logger.info(
            f"Starting test run: {self.config.load_test.num_clients} clients, "
            f"{self.config.load_test.total_requests} total requests"
        )

        requests_per_client = (
            self.config.load_test.total_requests // self.config.load_test.num_clients
        )

        # Create all client workers
        client_tasks = [
            self.client_worker(
                client_id=client_id,
                requests_per_client=requests_per_client,
            )
            for client_id in range(self.config.load_test.num_clients)
        ]

        # Run all clients concurrently
        await asyncio.gather(*client_tasks)

        async with httpx.AsyncClient() as client:
            count_response = await client.get(f"{self.config.server.url}/count")
            logger.info(f"Final counter value: {count_response.json()['count']}")

            stats_response = await client.get(f"{self.config.server.url}/stats")
            stats = StatsResponse(**stats_response.json())
            logger.info(
                f"Total Requests: {stats.total_requests}, Duration: {stats.duration_seconds}s"
            )
            logger.info(f"Average RPS: {stats.avg_rps}")
            logger.info(f"Min RPS: {stats.min_rps}, Max RPS: {stats.max_rps}")


async def main():
    config = Config.from_yaml("client_config.yaml")
    tester = CountTester(config)
    await tester.run()


if __name__ == "__main__":
    asyncio.run(main())
