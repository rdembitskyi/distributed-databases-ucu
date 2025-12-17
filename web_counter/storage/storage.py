from abc import ABC, abstractmethod


class CounterStorage(ABC):
    """Abstract interface for counter storage implementations."""

    @abstractmethod
    async def increment(self) -> int:
        """Increment the counter and return the new value."""
        pass

    @abstractmethod
    async def get_count(self) -> int:
        """Return the current counter value."""
        pass
