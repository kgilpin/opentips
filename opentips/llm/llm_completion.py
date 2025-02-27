import logging
import os
from typing import Any, Optional, TypeVar, Union, cast

from pydantic import BaseModel
from litellm import acompletion as litellm_completion, utils

logger = logging.getLogger(__name__)


class NoModelFoundError(Exception):
    pass


def get_model() -> str:
    """
    Determines the model to use based on the presence of environment variables.

    The function checks for specific environment variables corresponding to API keys
    (e.g., ANTHROPIC_API_KEY, DEEPSEEK_API_KEY) and selects a model accordingly.
    If no environment variable is set, an error is raised.

    Returns:
        str: The name of the model to use.

    Raises:
        NoModelFoundError: If no model is configured to use.
    """
    model_config = {
        "ANTHROPIC_API_KEY": "anthropic/claude-3-5-sonnet-20240620",
        "DEEPSEEK_API_KEY": "deepseek/deepseek-chat",
        "OPENAI_API_KEY": "gpt-4o",
        "GEMINI_API_KEY": "gemini/gemini-pro",
    }

    for env_key, model_name in model_config.items():
        if os.environ.get(env_key):
            logger.info(
                f"Found {env_key} so using {model_name} since no --model was specified."
            )
            return model_name

    raise NoModelFoundError("No LLM model is configured. Export an LLM key to use.")


T = TypeVar("T", bound=BaseModel)


async def complete(
    prompt: str,
    user_message: str,
    temperature: float,
    response_format: Optional[type[T]] = None,
) -> str:
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": user_message},
    ]
    model = get_model()

    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    if response_format is not None:
        kwargs["response_format"] = response_format

    response = cast(Any, await litellm_completion(**kwargs))
    logger.debug("Response: %r", response)

    response_content = response.choices[0].message.content
    assert isinstance(response_content, str)

    return response_content
