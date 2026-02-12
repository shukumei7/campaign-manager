"""Abstract base class for platform posters."""

from abc import ABC, abstractmethod


class BasePoster(ABC):
    """Base interface for posting content to a platform."""

    @abstractmethod
    def validate(self, title: str, body: str, **kwargs) -> list[str]:
        """Validate content before posting. Returns list of issues (empty = valid)."""
        ...

    @abstractmethod
    def post(self, title: str, body: str, **kwargs) -> dict:
        """Post content to platform. Returns dict with external_id and external_url."""
        ...

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if credentials are set up."""
        ...
