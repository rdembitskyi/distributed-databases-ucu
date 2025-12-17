import asyncio
from collections import defaultdict
import statistics
import time

from domain.stats import StatsResponse


class RequestTracker:
    """Tracks request timestamps to calculate RPS."""

    def __init__(self):
        self._timestamps = []
        self._lock = asyncio.Lock()

    async def record(self) -> None:
        """Record a request timestamp."""
        async with self._lock:
            self._timestamps.append(time.time())

    async def get_stats(self) -> StatsResponse:
        """Calculate RPS statistics."""
        async with self._lock:
            if not self._timestamps:
                return StatsResponse(
                    total_requests=0,
                    duration_seconds=0.0,
                    avg_rps=0.0,
                    min_rps=0,
                    max_rps=0,
                )

            total_requests = len(self._timestamps)
            start_time = self._timestamps[0]
            end_time = self._timestamps[-1]
            duration = end_time - start_time

            if duration == 0:
                return StatsResponse(
                    total_requests=total_requests,
                    duration_seconds=0.0,
                    avg_rps=0.0,
                    min_rps=0,
                    max_rps=0,
                )

            # Calculate RPS per second bucket
            buckets = defaultdict(int)
            for ts in self._timestamps:
                bucket = int(ts - start_time)
                buckets[bucket] += 1

            rps_values = list(buckets.values()) if buckets else [0]
            avg_rps = statistics.mean(buckets.values())

            return StatsResponse(
                total_requests=total_requests,
                duration_seconds=round(duration, 2),
                avg_rps=round(avg_rps, 2),
                min_rps=min(rps_values),
                max_rps=max(rps_values),
            )
