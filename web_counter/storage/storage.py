from abc import ABC, abstractmethod


class CounterStorage(ABC):
    """Abstract interface for counter storage implementations."""

    async def initialize(self):
        """Initialize the storage."""
        pass

    @abstractmethod
    async def increment(self) -> int:
        """Increment the counter and return the new value."""
        pass

    @abstractmethod
    async def get_count(self) -> int:
        """Return the current counter value."""
        pass
