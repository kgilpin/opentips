import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class EventBroadcaster:
    # Additional thread-safety on _instance is not needed, the singleton EventBroadcaster
    # is always created in the main thread.
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._event_queue: List[Dict[str, Any]] = []

    def enqueue_event(self, event_type: str, data: Dict):
        """Add an event to the queue"""
        event = {"type": event_type, "data": data}
        self._event_queue.append(event)

    def poll_events(self) -> List[Dict[str, Any]]:
        """Get and clear pending events"""
        events = self._event_queue
        self._event_queue = []
        return events


# Create global event broadcaster instance
event_broadcaster = EventBroadcaster()
