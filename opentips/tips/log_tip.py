import logging

from .rpc_types import Tip


def log_tip(
    logger: logging.Logger, log_level: int, message: str, tip: Tip, *, exc_info: bool
) -> None:
    logger.log(
        log_level,
        f"{message} - {tip.format_as_line()}",
        exc_info=exc_info,
    )
