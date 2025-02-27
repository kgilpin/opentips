import asyncio
from typing import Any, cast
import pytest
from pydantic import BaseModel

from opentips.comm.message_completion import (
    MessageCompletion,
    complete,
    complete_response,
)
from opentips.tips.event_broadcaster import event_broadcaster


class MockResponse(BaseModel):
    message: str
    value: int


class TestMessageCompletion:
    temperature = 0.1
    prompt = "the prompt"
    user_message = "the user message"

    @pytest.fixture
    def setup(self) -> MessageCompletion:
        # Create a new MessageCompletion instance for each test
        completion = MessageCompletion(timeout=1.0)
        # Clear any existing events
        event_broadcaster.poll_events()
        return completion

    @pytest.mark.asyncio
    async def test_complete_obj_success(self, setup):
        completion = setup
        test_response = MockResponse(message="test", value=42)

        # Start the completion in a task
        complete_task = asyncio.create_task(
            completion.complete(
                self.prompt, self.user_message, self.temperature, MockResponse
            )
        )

        # Wait for the event to be broadcast
        await asyncio.sleep(0.1)
        events = event_broadcaster.poll_events()

        assert len(events) == 1
        event = events[0]
        assert event["data"]["prompt"] == self.prompt
        assert event["data"]["user_message"] == self.user_message
        assert event["data"]["temperature"] == self.temperature
        assert event["data"]["response_format"] == MockResponse.model_json_schema()
        request_id = event["data"]["request_id"]

        # Simulate response
        completion.on_response(request_id, test_response)

        # Get the completion result
        result = await complete_task
        assert isinstance(result, MockResponse)
        assert result.message == "test"
        assert result.value == 42

    @pytest.mark.asyncio
    async def test_complete_str_success(self, setup):
        completion = setup
        test_response = "Hello, world!"

        # Start the completion in a task
        complete_task = asyncio.create_task(
            completion.complete(self.prompt, self.user_message, self.temperature)
        )

        # Wait for the event to be broadcast
        await asyncio.sleep(0.1)
        events = event_broadcaster.poll_events()

        assert len(events) == 1
        event = events[0]
        assert event["data"]["prompt"] == self.prompt
        assert event["data"]["user_message"] == self.user_message
        assert event["data"]["temperature"] == self.temperature
        assert "response_format" not in event["data"]
        request_id = event["data"]["request_id"]

        # Simulate response
        completion.on_response(request_id, test_response)

        # Get the completion result
        result = await complete_task
        assert isinstance(result, str)
        assert result == "Hello, world!"

    @pytest.mark.asyncio
    async def test_completion_timeout(self, setup):
        completion = setup
        completion.timeout = 0.1
        with pytest.raises(asyncio.TimeoutError):
            await completion.complete(self.prompt, self.user_message, self.temperature)

    @pytest.mark.asyncio
    async def test_helper_functions(self, setup):
        completion = setup
        test_response = MockResponse(message="test", value=42)

        # Test complete_obj helper
        complete_task = asyncio.create_task(
            complete(self.prompt, self.user_message, self.temperature, MockResponse)
        )

        await asyncio.sleep(0.1)
        events = event_broadcaster.poll_events()
        request_id = events[0]["data"]["request_id"]

        complete_response(request_id, cast(Any, test_response))

        result = await complete_task
        assert isinstance(result, MockResponse)
        assert result.message == "test"
        assert result.value == 42

        # Test complete_str helper
        complete_task = asyncio.create_task(
            complete(self.prompt, self.user_message, self.temperature, MockResponse)
        )

        await asyncio.sleep(0.1)
        events = event_broadcaster.poll_events()
        request_id = events[0]["data"]["request_id"]

        # Test complete_str_response helper
        complete_response(request_id, "Hello")

        result = await complete_task
        assert result == "Hello"
