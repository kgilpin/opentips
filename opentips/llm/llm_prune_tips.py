from typing import List, cast
import logging
from pydantic import BaseModel

from ..comm.completion import get_completion_handler, load_completion_response
from ..tips.rpc_types import Tip
from .settings import get_temperature

logger = logging.getLogger(__name__)


class LLMPrunedTips(BaseModel):
    retained_tips: List[str]  # List of tip IDs to retain


def tip_line(tip: Tip) -> str:
    header_line = (
        f"{tip.id} {tip.file}:{tip.line} - {tip.type} - {tip.label} - {tip.description}"
    )
    context = tip.context
    context = f"{context[:60]}..." if len(context) > 60 else context
    return "\n".join(["<|tip|>", header_line, context, "<|end-tip|>"])


DEFAULT_TEMPERATURE = 0.05
FACILITY_NAME = "prune_tips"
TEMPERATURE = get_temperature(FACILITY_NAME, DEFAULT_TEMPERATURE)


def llm_prune_tips_prompt() -> str:
    return f"""You are a programming assistant helping to manage a list of code improvement tips.

Return the tips in a resorted order, with the most valuable and diverse tips first.

Prioritize those that are:

1. Most actionable and valuable for improving the code
2. Represent a diverse set of improvement types
3. Cover different complexity levels
4. Avoid redundant or very similar suggestions

When there are similar or redundant suggestions, always choose just one to retain.

Respond with a list of tip IDs to retain, in JSON format like this:
{{"retained_tips": ["tip-id-1", "tip-id-2", ...]}}

Here are the available tips:
"""


async def llm_prune_tips(tips: list[Tip], tips_limit: int) -> list[Tip]:
    """
    Ask the LLM to select the most valuable and diverse tips up to the limit.

    Args:
        tips: List of tips to prune
        tips_limit: Maximum number of tips to retain

    Returns:
        List of retained tips
    """
    # Raises ValueError, which we will propagate.
    complete_fn = get_completion_handler()
    prompt = llm_prune_tips_prompt()
    tips_content = "\n".join([tip.model_dump_json() for tip in tips])
    try:
        prune_tips_data = await complete_fn(
            prompt, tips_content, TEMPERATURE, LLMPrunedTips
        )
        prune_tips = load_completion_response(prune_tips_data, LLMPrunedTips)
        return [tip for tip in tips if tip.id in prune_tips.retained_tips][:tips_limit]
    except Exception as e:
        logger.error(f"Error pruning tips: {str(e)}")
        # If there's an error, return all the tips
        return tips
