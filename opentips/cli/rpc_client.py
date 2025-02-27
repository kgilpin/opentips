import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Callable
from aiohttp import ClientSession

logger = logging.getLogger(__name__)


class RPCError(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.code}: {self.message}"


class RPCClient:
    def __init__(self, port: int = 5000, host: str = "localhost"):
        self.port = port
        self.host = host
        self.base_url = f"http://{host}:{port}"
        self.session: Optional[ClientSession] = None
        self._event_handlers: Dict[str, Callable] = {}
        self._poll_task: Optional[asyncio.Task] = None

    async def _poll_events(self):
        """Poll for server events"""
        while True:
            try:
                events = await self.call("poll_events")
                for event in events:
                    event_type = event["type"]
                    if event_type in self._event_handlers:
                        await self._event_handlers[event_type](event["data"])
            except Exception as e:
                logger.error(f"Event polling error: {e}")
            await asyncio.sleep(0.25)  # Poll interval. Consider exponential backoff.

    async def connect(self):
        """Connect to the RPC server"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

        # Start polling for events
        self._poll_task = asyncio.create_task(self._poll_events())

    async def disconnect(self):
        """Disconnect from the RPC server"""
        if self._poll_task:
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass

        if self.session:
            await self.session.close()
            self.session = None

        # Wait a brief moment to allow pending connections to close
        await asyncio.sleep(0.1)

    def on_event(self, event_type: str):
        """Decorator to register event handlers"""

        def decorator(func):
            self._event_handlers[event_type] = func
            return func

        return decorator

    async def call(self, method: str, **params) -> Dict:
        """Make an RPC call to the server"""
        if not self.session:
            raise RuntimeError("Client not connected")

        request = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

        async with self.session.post(f"{self.base_url}/rpc", json=request) as resp:
            response = await resp.json()
            if "error" in response:
                error_data = response["error"]
                raise RPCError(error_data["code"], error_data["message"])

            return response["result"]
