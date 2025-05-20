import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

REVIEW_FILENAME = "REVIEW.md"


def get_review_instructions(project_directory: Optional[Path] = None) -> Optional[str]:
    """
    Read the REVIEW.md file from the project directory if it exists.

    This file contains custom instructions for generating tips that will be
    incorporated into the prompt for the LLM.

    Args:
        project_directory: The directory to look for REVIEW.md in.

    Returns:
        The contents of the REVIEW.md file if it exists, otherwise None.
    """
    if project_directory is None:
        directory = Path.cwd()
    else:
        directory = project_directory
    review_path = directory / REVIEW_FILENAME

    if not review_path.is_file():
        logger.debug(f"No {REVIEW_FILENAME} found in {directory}")
        return None

    try:
        with open(review_path, "r") as file:
            content = file.read().strip()
            if content:
                logger.info(f"Found {REVIEW_FILENAME} with {len(content)} characters")
                return content
            else:
                logger.debug(f"{REVIEW_FILENAME} exists but is empty")
                return None
    except Exception as e:
        logger.warning(f"Error reading {REVIEW_FILENAME}: {str(e)}")
        return None
