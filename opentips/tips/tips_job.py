import asyncio
import logging
from typing import Optional

from opentips.tips.prune_tips import prune_tips
from opentips.tips.storage import list_tips

from .invalidate_tips import invalidate_tips
from .diff import diff
from .event_broadcaster import event_broadcaster
from .fetch_tips import fetch_tips_for_diff
from .rpc_types import TipList

logger = logging.getLogger(__name__)


class TipsJob:
    def __init__(self, delay: int, tips_limit: int):
        """Initialize TipRequest with configurable delay

        Args:
            delay: Time in seconds to wait before processing tip request
            tips_limit: The maximum number of tips to retain
        """
        self._delay = delay
        self._tips_limit = tips_limit
        self._current_task: Optional[asyncio.Task] = None

    def schedule(self):
        """Schedule a new tip request, canceling any existing one"""
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()

        async def delayed_tip():
            try:
                await asyncio.sleep(self._delay)

                return await self.process_tips()
            except asyncio.CancelledError:
                logger.info("Tip request was canceled")
            except Exception as e:
                logger.error(f"An error occurred in delayed_tip: {e}", exc_info=True)

        self._current_task = asyncio.create_task(delayed_tip())
        return self._current_task

    async def process_tips(self) -> TipList:
        """Process the tip request"""
        diff_chunks = diff(new_only=True)
        # Return early if diff_chunks is None or, more likely, an empty list
        if not diff_chunks:
            logger.debug("No diff content to analyze")
            return TipList(tips=[])

        changed_files = {chunk.to_file for chunk in diff_chunks}
        invalidate_tips(list_tips(), changed_files=changed_files)

        tip_list = await fetch_tips_for_diff(diff_chunks)

        tips = invalidate_tips(tip_list.tips)
        tips = await prune_tips(tips, self._tips_limit)

        tip_list.tips = tips

        logger.info("Tips:")
        for tip in tip_list.tips:
            logger.info(str(tip))

        event_broadcaster.enqueue_event("tips", tip_list.model_dump())

        return tip_list
