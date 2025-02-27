from dataclasses import dataclass
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, cast
from pydantic import ValidationError

from ..comm.completion import get_completion_handler, load_completion_response
from ..tips.rpc_types import Tip
from ..tips.git import DiffChunk
from .settings import get_temperature

logger = logging.getLogger(__name__)


class LLMTip(BaseModel):
    file: str
    line: int
    type: str
    context: str
    complexity: str
    label: str
    description: str


class LLMTipList(BaseModel):
    tips: List[LLMTip]


@dataclass
class FileChunk:
    file_name: str
    start_line: int
    end_line: int
    content: str


DEFAULT_TEMPERATURE = 0.05
FACILITY_NAME = "tips"
TEMPERATURE = get_temperature(FACILITY_NAME, DEFAULT_TEMPERATURE)


async def llm_tips(
    diff_chunks: Optional[list[DiffChunk]], file_chunk: Optional[FileChunk]
) -> LLMTipList:
    # Raises ValueError, which we will propagate.
    complete_fn = get_completion_handler()

    # There must be either a diff or a file chunk
    if not diff_chunks and not file_chunk:
        raise ValueError("No diff or file chunk provided to llm_tips")

    base_instructions = f"""You are a helpful programming assistant. Please analyze this git diff and suggest 1-3 specific, actionable changes
that would make the code better. 

Don't nit-pick style or formatting issues, or ask the user to add cases or complexity to handle situations that
aren't acutally observed in the code.

Don't suggest tips that have already been considered by the developer and are explained in the comments.

Respect implementation decisions that are explained in comments, including both current choices and future plans that are explicitly deferred.

Don't suggest switching the implementation of some code back to the way that it previously was.

Don't emit the following types of suggestions:

<|notips|>
Changes to the number of newlines or whitespace lines
<|end-notips|>
"""

    diff_instructions = None
    user_message: str = ""
    if diff_chunks:
        diff_content = "\n".join((chunk.chunk for chunk in diff_chunks))
        logger.info(f"Analyzing diff content:\n{diff_content}")
        diff_instructions = """The user is working on the following diff:"""
        user_message = diff_content

    chunk_instructions = None
    if file_chunk:
        file_content_with_line_numbers = "\n".join(
            [
                f"{i+1:05d}: {line}"
                for i, line in enumerate(file_chunk.content.split("\n"))
            ]
        )
        logger.info(f"Analyzing file chunk content:\n{file_content_with_line_numbers}")
        chunk_instructions = """The user is working on the following file:"""
        user_message = f"""<|file-name|>
{file_chunk.file_name}
<|end-file-name|>
<|file|>
{file_content_with_line_numbers}
<|end-file|>
"""

    examples = """Provide the following information about each tip, in the provided JSON schema format:

file: the path to the file from the project root.
line: line number in the file where the tip applies.
type: the type of code improvement that the tip suggests.
context: a snippet of code that provides the context for the tip. It should exactly match the code in the file
    that the user is working on.
complexity: one of "low", "medium", or "high". It advises the programmer about 
    how much expertise is required to understand and apply the tip.
label: a few words that concicely describe the tip.
description: a sentence that explain the tip and how it would make an improvement to the code.
"""

    prompt = (
        [base_instructions]
        + [instr for instr in (diff_instructions, chunk_instructions) if instr]
        + [examples]
    )

    assert user_message != "", "User message must be provided"

    # Despite the prompt, the LLM keeps providing a PATH that is only the filename and not the full path
    def is_directory_path(tip: Tip):
        path_components = Path(tip.file).parts
        return len(path_components) > 1

    try:
        tip_list_data = await complete_fn(
            "\n\n".join(prompt), user_message, TEMPERATURE, LLMTipList
        )
        tip_list = load_completion_response(tip_list_data, LLMTipList)
    except ValidationError as e:
        logger.error(f"Error validating LLM response: {e}")
        # No-arg constructor is not valid for TipList
        return LLMTipList(tips=[])
    except Exception as e:
        logger.error(f"Error getting LLM tips: {str(e)}")
        return LLMTipList(tips=[])

    for tip in tip_list:
        if isinstance(tip, Tip):
            if not is_directory_path(tip):
                logger.warning(f"Tip file path is not a full path: {tip.file}")

    return tip_list
