import logging
from typing import Optional, cast
from pydantic import ValidationError

from ..llm.settings import get_temperature
from ..comm.completion import get_completion_handler
from ..tips.rpc_types import Tip
from ..tips.git import DiffChunk

logger = logging.getLogger(__name__)

DEFAULT_TEMPERATURE = 0.05
FACILITY_NAME = "describe_tip"
TEMPERATURE = get_temperature(FACILITY_NAME, DEFAULT_TEMPERATURE)


async def llm_describe_tip(tip: Tip, diff_chunks: list[DiffChunk]) -> Optional[str]:
    complete_fn = get_completion_handler()

    diff_content = "\n".join((chunk.chunk for chunk in diff_chunks))

    base_instructions = f"""You are a helpful programming assistant. 

A user has requested an explanation of a tip. Please provide a detailed explanation of the tip.
Just provide the explanation, don't begin with a greeting or any other text.

The user is working on the following diff:

<|diff|>
{diff_content}
<|end-diff|>

Here's the tip:
"""
    prompt = [base_instructions]
    user_message = tip.model_dump_json()
    try:
        return cast(
            str, await complete_fn("\n\n".join(prompt), user_message, TEMPERATURE, None)
        )
    except ValidationError as e:
        logger.error(f"Error validating LLM response: {e}")
        return None
    except Exception as e:
        logger.error(f"Error describing tip: {str(e)}")
        return None
