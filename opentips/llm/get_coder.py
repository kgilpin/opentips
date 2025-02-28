import importlib
import sys

from .llm_completion import get_model


def get_coder(file_names, chat_history_file, temperature, *, dry_run=False):
    """
    Get an instance of aider to work with the given LLM `model` at `temperature`.
    Will store the markdown chat logs in
    the `chat_history_file`.

    Aider is loaded as a runtime dependency and not required in requirements.txt.
    """
    try:
        # Dynamically import aider modules at runtime
        aider_coders = importlib.import_module("aider.coders")
        aider_models = importlib.import_module("aider.models")
        aider_io = importlib.import_module("aider.io")
    except ImportError:
        raise ImportError(
            "aider-chat is required for this operation, but it's not installed"
        )

    model = aider_models.Model(get_model())

    io = aider_io.InputOutput(
        yes=True,  # Say yes to every suggestion aider makes
        chat_history_file=chat_history_file,  # Log the chat here
        input_history_file="/dev/null",  # Don't log the "user input"
    )

    coder = aider_coders.Coder.create(
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
