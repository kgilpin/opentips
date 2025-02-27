import pytest
import asyncio
from opentips.cli.rpc_server import RPCServer
from opentips.cli.rpc_client import RPCClient


class TestRPCServer:
    @pytest.fixture
    async def setup(self):
        server = RPCServer(port=0)
        try:
            await server.start_server()
            port = server.assigned_port
            assert port is not None

            client = RPCClient(port=port)
            try:
                await client.connect()
                yield server, client
            finally:
                await client.disconnect()
        finally:
            await server.stop()

    @pytest.mark.asyncio
    async def test_echo_and_events(self, setup):
        server, client = setup

        # Set up event tracking
        received_events = []
        echo_event = asyncio.Event()

        @client.on_event("echo")
        async def handle_echo(data):
            received_events.append(("echo", data))
            echo_event.set()

        # Send echo message
        test_message = "hello world"
        response = await client.call("echo", message=test_message)

        # Wait for echo event
        await asyncio.wait_for(echo_event.wait(), timeout=1.0)

        # Poll for events
        events = await client.call("poll_events")

        # Verify response and events
        assert response == test_message
        assert len(received_events) == 1
        assert received_events[0][0] == "echo"
        assert received_events[0][1]["message"] == test_message
        assert len(events) == 0  # Events should be cleared after polling
