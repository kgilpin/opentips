from dataclasses import dataclass
import logging
from typing import Optional


from .rpc_types import Patch, Tip
from ..llm.get_coder import get_coder

logger = logging.getLogger(__name__)

CHAT_HISTORY_FILE = "chat_history.txt"
TEMPERATURE = 0


def apply_tip(tip: Tip, *, dry_run=False) -> Optional[list[Patch]]:
    """Apply a tip"""

    file_names = [tip.file]
    coder = get_coder(file_names, CHAT_HISTORY_FILE, TEMPERATURE, dry_run=dry_run)

    try:
        coder.run(tip.description)
        raw_edits = coder.get_edits()
        edits: list[Patch] = []
        for raw_edit in raw_edits:
            (file_name, search, replace) = raw_edit
            edits.append(Patch(file_name=file_name, search=search, replace=replace))

        return edits
    except Exception as coder_err:
        # swallow any exceptions during benchmarking
        logger.warning(coder_err)
        return None
