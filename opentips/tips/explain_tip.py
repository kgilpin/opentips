from typing import Optional

from opentips.tips.rpc_types import Tip

from .diff import diff
from ..llm.llm_describe_tip import llm_describe_tip


async def explain_tip(tip: Tip) -> Optional[str]:
    """Explain a tip"""
    print(f"Explaining tip: {tip.model_dump()}")

    diff_chunks = diff()
    if diff_chunks is None:
        return None

    return await llm_describe_tip(tip, diff_chunks)
