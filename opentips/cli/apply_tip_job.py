import logging
from typing import Optional, List

from ..tips.event_broadcaster import event_broadcaster
from ..tips.rpc_types import Patch, Tip
from ..tips.apply_tip import apply_tip as apply_tip_fn
from ..tips.storage import delete_tip as delete_tip_fn


logger = logging.getLogger(__name__)


class ApplyTipJob:
    def __init__(self, tip: Tip):
        """Initialize ApplyTipJob with a tip to apply

        Args:
            tip: The tip to apply
        """
        self.tip = tip

    async def apply(
        self, *, dry_run=False, delete_after_apply: Optional[bool]
    ) -> Optional[List[Patch]]:
        """
        Apply the tip.

        Optionally perform a dry run and/or delete the tip after successful application.
        """
        if delete_after_apply is None:
            delete_after_apply = not dry_run

        patches = apply_tip_fn(self.tip, dry_run=dry_run)

        if delete_after_apply:
            deletion_success = delete_tip_fn(self.tip.id)
            if deletion_success:
                event_broadcaster.enqueue_event(
                    "tip_deleted", {"tip_id": self.tip.id, "reason": "applied"}
                )
            else:
                logger.warning(f"Failed to delete tip {self.tip.id} after application")

        if not patches or len(patches) == 0:
            return None

        event_broadcaster.enqueue_event(
            "patches",
            {
                "tip_id": self.tip.id,
                "patches": [patch.model_dump() for patch in patches],
            },
        )
