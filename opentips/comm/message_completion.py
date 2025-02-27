import asyncio
import logging
import os
from typing import Dict, Generic, Optional, TypeVar, Any, Union
from uuid import uuid4

from pydantic import BaseModel

from ..tips.event_broadcaster import event_broadcaster

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")

DEFAULT_TIMEOUT = 120


class MessageCompletion(Generic[T]):
    """
    To make testability easier, the MessageCompletion class is not a singleton.
    """

    def __init__(self, timeout: float = DEFAULT_TIMEOUT):
        self.timeout = timeout

        self._pending_responses: Dict[str, asyncio.Event] = {}
        self._results: Dict[str, Any] = {}

    def on_response(self, request_id: str, response: T) -> None:
        self._results[request_id] = response
        if request_id in self._pending_responses:
            self._pending_responses[request_id].set()

    async def complete(
        self,
        prompt: str,
        user_message: str,
        temperature: float,
        response_format: Optional[type[T]] = None,
    ) -> T:
        request_id = str(uuid4())
        params = {
            "request_id": request_id,
            "directory": os.getcwd(),
            "prompt": prompt,
            "user_message": user_message,
            "temperature": temperature,
        }
        if response_format:
            params["response_format"] = response_format.model_json_schema()

        logger.info("[message-completion] Completing message: %r", params)

        event = asyncio.Event()
        self._pending_responses[request_id] = event
        event_broadcaster.enqueue_event("complete", params)

        try:
            await asyncio.wait_for(event.wait(), timeout=self.timeout)
            return self._results.pop(request_id)
        finally:
            self._pending_responses.pop(request_id, None)
            self._results.pop(request_id, None)


completion = MessageCompletion()


async def complete(
    prompt: str,
    user_message: str,
    temperature: float,
    response_format: Optional[type[T]],
) -> str:
    return await completion.complete(prompt, user_message, temperature, response_format)


def complete_response(request_id: str, response: Union[str, type[T]]) -> None:
    completion.on_response(request_id, response)
