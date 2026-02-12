"""Abstract base class for platform trackers."""

from abc import ABC, abstractmethod


class BaseTracker(ABC):
    """Base interface for tracking post metrics."""

    @abstractmethod
    def fetch_metrics(self, external_id: str) -> dict:
        """Fetch current metrics. Returns dict with upvotes, comments, views, extra."""
        ...
