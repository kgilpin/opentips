import logging
from typing import Any, Callable

from opentips.tips.rpc_types import Tip
from .log_tip import log_tip


def tip_operation(
    logger: logging.Logger, message: str, tip: Tip, fn: Callable[[Tip], Any]
) -> Any:
    try:
        return fn(tip)
    except Exception:
        log_tip(logger, logging.WARNING, message, tip, exc_info=True)
        return None
