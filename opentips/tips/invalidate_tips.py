import logging
from typing import List, Optional, Set

from opentips.tips.rpc_types import Tip
from opentips.tips.tip_operation import tip_operation

from .log_tip import log_tip
from .event_broadcaster import event_broadcaster
from .match_tip_in_file import match_tip_in_file
from .storage import delete_tip, list_tips, update_tip

logger = logging.getLogger(__name__)


def invalidate_tips(
    tips: List[Tip], *, changed_files: Optional[Set[str]] = None
) -> List[Tip]:
    """
    Invalidate tips based on the diff content.

    Args:
        tips: The list of tips to check
        diff_chunks: The diff content

    Returns:
        A list of valid tips
    """
    if changed_files is None:
        changed_files = set([tip.file for tip in tips])

    # Use a list here in order to preserve tip order, and because Tip is not hashable
    tips_applicable_to_changed_file = [tip for tip in tips if tip.file in changed_files]
    valid_tips = [tip for tip in tips if tip not in tips_applicable_to_changed_file]
    for tip in tips_applicable_to_changed_file:
        line = match_tip_in_file(tip)
        if line is not None:
            if line != tip.line:
                log_tip(
                    
                    logger,
                    logging.INFO,
                    f"Tip line changed from {tip.line} to {line}",
                    tip,
                    exc_info=False,
                )
                tip.line = line
                tip_operation(
                    logger,
                    "Failed to update tip",
                    tip,
                    update_tip,
                )
            valid_tips.append(tip)
        else:
            log_tip(
                logger,
                logging.INFO,
                "Tip no longer applies",
                tip,
                exc_info=False,
            )
            if tip_operation(
                logger,
                "Failed to delete tip",
                tip,
                lambda tip: delete_tip(tip.id),
            ):
                event_broadcaster.enqueue_event(
                    "tip_deleted", {"tip_id": tip.id, "reason": "invalidated"}
                )

    return valid_tips
