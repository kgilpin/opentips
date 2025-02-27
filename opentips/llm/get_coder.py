from aider.coders import Coder
from aider.models import Model
from aider.io import InputOutput

from .llm_completion import get_model


# For reference, see: https://github.com/Aider-AI/aider-swe-bench/blob/6e98cd6c3b2cbcba12976d6ae1b07f847480cb74/harness.py#L132
# Apache License Version 2.0
def get_coder(file_names, chat_history_file, temperature, *, dry_run=False) -> Coder:
    """
    Get an instance of aider to work with the given LLM `model` at `temperature`.
    Will store the markdown chat logs in
    the `chat_history_file`.
    """
    model = Model(get_model())

    io = InputOutput(
        yes=True,  # Say yes to every suggestion aider makes
        chat_history_file=chat_history_file,  # Log the chat here
        input_history_file="/dev/null",  # Don't log the "user input"
    )

    coder = Coder.create(
        main_model=model,
        io=io,
        map_tokens=2048,
        stream=False,
        auto_commits=False,
        fnames=file_names,
        dry_run=dry_run,
    )
    coder.temperature = temperature

    # Take at most 4 steps before giving up.
    # Usually set to 5, but this reduces API costs.
    coder.max_reflections = 4

    # Add announcement lines to the markdown chat log
    coder.show_announcements()

    return coder
