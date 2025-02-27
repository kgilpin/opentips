from typing import List
import logging

from ..llm.llm_prune_tips import llm_prune_tips
from .event_broadcaster import event_broadcaster
from .log_tip import log_tip
from .rpc_types import Tip
from .storage import delete_tip as delete_tip_fn
from .tip_operation import tip_operation

logger = logging.getLogger(__name__)


def prune_tip(tip: Tip):
    """
    Prune a tip by logically deleting it and broadcasting a tip_deleted event.
    """
    if delete_tip_fn(tip.id):
        log_tip(
            logger,
            logging.INFO,
            f"Pruning tip based on priority",
            tip,
            exc_info=False,
        )
        event_broadcaster.enqueue_event(
            "tip_deleted", {"tip_id": tip.id, "reason": "pruned"}
        )


async def prune_tips(tips: List[Tip], tips_limit: int) -> List[Tip]:
    """
    Prune tips to maintain the configured limit. Tips are pruned based on priority
    and uniqueness.

    Args:
        tips: The list of tips to prune
        tips_limit: The maximum number of tips to keep

    Returns:
        A list of pruned tips
    """
    if len(tips) <= tips_limit:
        return tips

    selected_tips = await llm_prune_tips(tips, tips_limit)
    # Array sizes are small and tips are not hashable, so we stick with a list
    tips_to_remove = [tip for tip in tips if tip not in selected_tips]

    for tip in tips_to_remove:
        tip_operation(
            logger,
            "Error pruning tip",
            tip,
            lambda tip: prune_tip(tip),
        )

    return selected_tips
