import logging
from typing import Optional
from pathlib import Path

from .rpc_types import Tip


logger = logging.getLogger(__name__)


SEARCH_RADIUS = 20


def match_tip_in_file(tip: Tip) -> Optional[int]:
    """
    Match a tip in a file.

    Scan a range of lines around the tip's line number to find the tip in the file.
    Returns None if the file cannot be read or if the tip is not found.
    """
    try:
        file_content = Path(tip.file).read_text()
    except (IOError, FileNotFoundError) as e:
        logger.warning(
            f"[match-tip-in-file] Error reading file {tip.file}", exc_info=True
        )
        return None

    lines = file_content.split("\n")
    start_line = max(0, tip.line - SEARCH_RADIUS)
    end_line = min(len(lines), tip.line + SEARCH_RADIUS)
    tip_context_start_line = tip.context.split("\n")[0]

    # Use enumerate to iterate over line numbers and content together
    for i, line in enumerate(lines[start_line:end_line], start=start_line):
        if line.strip() == tip_context_start_line:
            return i + 1

    return None
