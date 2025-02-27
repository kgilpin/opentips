from json import loads, JSONDecodeError
import logging
import os
from typing import cast
from jsonrpcserver import Error, Success, async_dispatch
import asyncio
from aiohttp import web
from functools import wraps

from opentips.tips.rpc_types import OpenTipsRPC
from opentips.tips.storage import TipNotFoundError

from .rpc_provider import RPCProvider

logger = logging.getLogger(__name__)

"""
Time in seconds to wait for code edits to stop before starting to discover tips.
"""
DEFAULT_TIP_DELAY = 15

"""
Maximum number of tips to retain.
"""
DEFAULT_TIPS_LIMIT = 7


def _get_opentips_setting(setting_name: str, default_value: int) -> int:
    """
    Get an OpenTips setting from the environment.

    Args:
        setting_name: The name of the setting
        default_value: The default value to use if the setting is not found or invalid

    Returns:
        The setting value
    """
    env_var_name = f"OPENTIPS_{setting_name.upper()}"
    setting_value = os.getenv(env_var_name)
    if setting_value is None:
        return default_value

    try:
        return int(setting_value)
    except ValueError:
        logger.warning(f"Invalid value for {env_var_name}: {setting_value}")
        return default_value


def get_tips_delay() -> int:
    """
    Get the delay before starting to discover tips from the environment.
    """
    return _get_opentips_setting("TIP_DELAY", DEFAULT_TIP_DELAY)


def get_tips_limit() -> int:
    """
    Get the maximum number of tips to retain from the environment.
    """
    return _get_opentips_setting("TIPS_LIMIT", DEFAULT_TIPS_LIMIT)


def wrap_method_as_rpc(method):
    """
    Wrap a function as an RPC method

    Call the method. If the method is a coroutine, await it.
    If the method succeeds, return RPC Success. Otherwise, wrap
    the error in RPC Error.
    """

    @wraps(method)
    async def wrapped_method(*args, **kwargs):
        try:
            # Check if the method is a coroutine function
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)

            # model_dump() the result, otherwise pass it as-is
            if hasattr(result, "model_dump"):
                response_obj = result.model_dump()
            # model_dump() a list of objects
            elif isinstance(result, list) and all(
                hasattr(obj, "model_dump") for obj in result
            ):
                response_obj = [obj.model_dump() for obj in result]
            else:
                response_obj = result
            return Success(response_obj)
        except Exception as e:
            error_class_name = e.__class__.__name__
            error_message = str(e)

            logger.exception("Exception in RPC method")

            code = 500
            if isinstance(e, TipNotFoundError):
                code = 404
            return Error(code, f"{error_class_name}: {error_message}")

    return wrapped_method


access_logger = logging.getLogger("aiohttp.access")
access_logger.setLevel(logging.WARNING)


log_poll_events_fn = lambda: logger.debug("poll_events")
log_method_fn = lambda payload: logger.info(
    f"{payload['method']} {payload.get('params', '')}"
)
log_error_fn = lambda request_text: logger.warning(
    f"Invalid or unparseable RPC request: {request_text}"
)


class RPCServer:
    def __init__(
        self,
        *,
        host: str = "localhost",
        port: int = 0,
        tip_delay=get_tips_delay(),
        tips_limit=get_tips_limit(),
    ):
        self.host = host
        self.port = port
        self.assigned_port = None
        self.running = False
        self.app = web.Application(logger=access_logger)
        self.app.router.add_post("/rpc", self.handle_rpc)
        self.provider: OpenTipsRPC = RPCProvider(
            tip_delay=tip_delay,
            tips_limit=tips_limit,
        )
        # Create a dictionary of methods from the provider instance
        self.methods = {
            name: wrap_method_as_rpc(getattr(self.provider, name))
            for name in dir(self.provider)
            if not name.startswith("_")  # Skip private methods
        }

    async def handle_rpc(self, request: web.Request) -> web.Response:
        """Handle RPC requests"""
        request_text = await request.text()

        try:
            payload = loads(request_text)
            if "method" in payload:
                if payload["method"] == "poll_events":
                    log_poll_events_fn()
                else:
                    log_method_fn(payload)

        except JSONDecodeError:
            log_error_fn(request_text)
            return web.json_response(
                {"error": {"code": 400, "message": "Invalid JSON"}}, status=400
            )
        except KeyError:
            log_error_fn(request_text)
            return web.json_response(
                {"error": {"code": 400, "message": "Missing required field(s)"}},
                status=400,
            )

        response = await async_dispatch(request_text, methods=self.methods)
        return web.Response(text=str(response), content_type="application/json")

    async def start_server(self):
        # web.run_app has been recommended as a simpler way to run the server, but I am not sure
        # how I would obtain the port number assigned by the OS. Similarly for asyncio.start_server;
        # the code as written handles getting the OS-assigned port, which is needed when port=0.
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        self.running = True

        # Consider using app.on_startup to get the server instance directly
        if not isinstance(site._server, asyncio.Server):
            raise RuntimeError(
                f"Expecting site to be an instance of asyncio.Server, got {site._server}"
            )

        server = cast(asyncio.Server, site._server)

        # Access and log the actual port assigned by the OS
        sockets = server.sockets
        if server.sockets:
            self.assigned_port = sockets[0].getsockname()[1]
            print(f"OpenTips running on {self.host}:{self.assigned_port}")
            logger.info(f"OpenTips running on {self.host}:{self.assigned_port}")
        else:
            raise RuntimeError(
                f"Server started, but no sockets found so the port cannot be determined"
            )

    async def stop(self):
        """Stop the server"""
        if self.running:
            logger.info("Stopping RPC server")
            self.running = False
