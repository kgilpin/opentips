import logging
import os
from itertools import islice
from pathlib import Path

from opentips.tips.rpc_types import Tip, TipList
from opentips.tips.git import DiffChunk


from ..llm.llm_tips import FileChunk, LLMTipList, llm_tips
from .storage import save_tip_if_new
from .review import get_review_instructions

logger = logging.getLogger(__name__)


async def fetch_tips_for_diff(diff: list[DiffChunk]) -> TipList:
    """
    Get programming tips based on the the current project diff.

    Returns:
        A list of programming tips relevant to the diff content
    """
    logger.debug("Fetching tips for diff %s", diff)

    # Get project-specific review instructions from REVIEW.md if available
    review_instructions = get_review_instructions()
    if review_instructions:
        logger.info(f"Found REVIEW.md with instructions for tip generation")

    llm_tip_list = await llm_tips(diff, None, review_instructions)
    return collect_tip_list(llm_tip_list)


async def fetch_tips_for_file_range(
    file_name: str, start_line: int, end_line: int
) -> TipList:
    """
    Get programming tips based on the provided file range.

    Args:
        file_name: The file to analyze
        start_line: The starting line number
        end_line: The ending line number

    Returns:
        A list of programming tips relevant to the file range
    """

    logger.debug(
        "Fetching tips for file range %s:%d-%d", file_name, start_line, end_line
    )

    # Get project-specific review instructions from REVIEW.md if available
    review_instructions = get_review_instructions()
    if review_instructions:
        logger.info(f"Found REVIEW.md with instructions for tip generation")

    if not Path(file_name).is_file():
        logger.error(f"File not found or is not a regular file: {file_name}")
        # We treat this error beningly because the user may have deleted the file
        return TipList(
            tips=[], error=f"File not found or is not a regular file: {file_name}"
        )

    with open(file_name) as f:
        file_content = "".join(islice(f, start_line - 1, end_line))

    file_chunk = FileChunk(
        file_name=file_name,
        start_line=start_line,
        end_line=end_line,
        content=file_content,
    )
    llm_tip_list = await llm_tips(None, file_chunk, review_instructions)
    return collect_tip_list(llm_tip_list)


def collect_tip_list(llm_tip_list: LLMTipList) -> TipList:
    """
    Collect and save tips from the LLMTipList. Each tip is loaded from the raw
    LLM tip data into a Tip object, which is then saved to disk if it is new.
    """
    tip_list = TipList(tips=[])
    for llm_tip in llm_tip_list.tips:
        tip = Tip.model_construct(**llm_tip.model_dump())
        tip.directory = os.getcwd()
        if save_tip_if_new(tip):
            logger.info(f"Obtained tip '{tip.label}' for:\n{tip.context}")
            tip_list.tips.append(tip)

    return tip_list
