from base64 import urlsafe_b64encode
import base64
from hashlib import sha256
import itertools
import json
import logging
import os
from pathlib import Path
from typing import List, Optional

from opentips.tips.rpc_types import Tip
from opentips.tips.git import DiffChunk

logger = logging.getLogger(__name__)


def default_base_storage_dir() -> Path:
    # Obtain from Path.home() or from the environment
    base_storage_dir = os.environ.get("OPENTIPS_STORAGE_DIR")
    if not base_storage_dir:
        base_storage_dir = Path.home() / ".opentips"

    return Path(base_storage_dir)


BASE_STORAGE_DIR = default_base_storage_dir()


# Set the base storage directory for tips. This is used for testing.
def set_base_storage_dir(path: Path):
    global BASE_STORAGE_DIR
    BASE_STORAGE_DIR = path


class TipNotFoundError(Exception):
    pass


def get_storage_dir(subdir: str) -> Path:
    """Get the storage directory for tips, creating it if it doesn't exist.

    Returns:
        Path: The path to the tips storage directory
    """
    storage_dir = BASE_STORAGE_DIR / subdir
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir


def build_tip_digest(tip: Tip) -> str:
    """Generate a unique ID for a tip.

    Args:
        tip: The tip to generate an ID for

    Returns:
        str: A unique ID for the tip
    """
    # Build a digest from the tip content and encode it
    json_bytes = json.dumps(
        {k: getattr(tip, k) for k in ["file", "line", "label"]}, sort_keys=True
    ).encode("utf-8")
    hash_bytes = sha256(json_bytes).digest()
    return base64.urlsafe_b64encode(hash_bytes).rstrip(b"=").decode("ascii")


def build_tip_external_id(tip_id: str, directory: str) -> str:
    """Build an external ID for a tip.

    Args:
        tip_id: The internal ID of the tip
        directory: The directory the tip is in

    Returns:
        str: The external ID for the tip
    """
    id_parts = (
        "1.0".encode("utf-8"),
        directory.encode("utf-8"),
        tip_id.encode("utf-8"),
    )
    return base64.urlsafe_b64encode(b"\n".join(id_parts)).rstrip(b"=").decode("ascii")


def parse_tip_external_id(external_id: str) -> tuple[str, str]:
    """Parse an external ID into its constituent parts.

    Args:
        external_id: The external ID to parse

    Returns:
        tuple[str, str]: The directory and internal ID of the tip
    """
    decoded_id = base64.urlsafe_b64decode(external_id + "===").decode("utf-8")
    tokens = decoded_id.split("\n")
    version = tokens[0]
    if version != "1.0":
        raise ValueError(f"Invalid tip ID format: {tokens[0]}")

    if len(tokens) != 3:
        raise ValueError(f"Invalid tip ID: {external_id}")

    return tokens[1], tokens[2]


def is_diff_chunk_new(diff_chunk: DiffChunk) -> bool:
    """Check if a diff chunk has been previously observed or not.
    As a side effect, save the diff chunk to storage if it is new.

    Args:
        diff_chunk: The diff chunk to check

    Returns:
        bool: True if the diff chunk is new, False if it has been seen before
    """
    storage_dir = get_storage_dir("diffs")
    diff_digest = diff_chunk.digest()
    diff_path = storage_dir / f"{diff_digest}"

    if diff_path.exists():
        logger.debug(f"Skipping existing diff {diff_digest}")
        return False

    logger.debug(f"Saving new diff {diff_digest}")
    diff_path.write_text(diff_chunk.chunk)

    return True


def save_tip_if_new(tip: Tip) -> bool:
    """Save a tip to storage if it doesn't already exist.

    A tip is considered new if there is no tip with the same ID in the same directory.

    Args:
        tip: The tip to save

    Returns:
        bool: True if the tip was saved, False if it already existed

    Raises:
        IOError: If there's an error writing the tip to storage
        PermissionError: If there's a permission error when writing the tip
        UnicodeEncodeError: If there's an encoding error with the directory name
    """
    storage_dir = get_storage_dir("tips")
    tip_digest = build_tip_digest(tip)

    tip_directory_encoded = urlsafe_b64encode(
        tip.directory.encode("utf-8", errors="ignore")
    ).decode("ascii")

    tip_dir = storage_dir / tip_directory_encoded
    tip_dir.mkdir(exist_ok=True)
    tip_path = tip_dir / f"{tip_digest}.json"

    if tip_path.exists():
        return False

    tip.id = build_tip_external_id(tip_digest, tip.directory)
    try:
        tip_path.write_text(json.dumps(tip.model_dump(), indent=2))
    except (IOError, PermissionError) as e:
        logger.error(f"Failed to save tip {tip_digest}: {e}")
        raise

    return True


def update_tip(tip: Tip) -> bool:
    """Update a tip in storage.

    Args:
        tip: The tip to update

    Returns:
        bool: True if the tip was updated, False if the tip was not found
    """

    tip_id = tip.id
    storage_dir = get_storage_dir("tips")
    _, tip_digest = parse_tip_external_id(tip_id)
    tip_path = next(storage_dir.glob(f"*/{tip_digest}.json"), None)

    if tip_path is None:
        return False

    try:
        tip_path.write_text(json.dumps(tip.model_dump(), indent=2))
    except (IOError, PermissionError) as e:
        logger.error(f"Failed to save tip {tip_digest}: {e}")
        raise

    return True


# TODO: Consider adding a sorting option.
def list_tips(
    limit: Optional[int] = None, *, include_deleted: bool = False
) -> List[Tip]:
    """List all tips in a directory.

    Args:
        limit: The maximum number of tips to return
        include_deleted: Whether to include logically
            deleted tips in the list

    Returns:
        list[Tip]: The list of tips in the directory
    """
    directory = os.getcwd()
    storage_dir = get_storage_dir("tips")
    tip_directory_encoded = urlsafe_b64encode(directory.encode("utf-8")).decode("ascii")
    tip_dir = storage_dir / tip_directory_encoded

    if not tip_dir.exists():
        return []

    def read_tip(tip_path):
        try:
            with open(tip_path, "r") as f:
                tip_data = json.load(f)
                tip = Tip.model_validate(tip_data)
                if not tip.deleted or include_deleted:
                    return tip

                return None
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load tip {tip_path}: {e}")

    tip_files = tip_dir.glob("*.json")
    tips = (read_tip(tip_file) for tip_file in tip_files)
    tips = filter(None, tips)

    if limit is not None:
        return list(itertools.islice(tips, limit))
    else:
        return list(tips)


def load_tip(tip_id: str, *, include_deleted: bool = False) -> Tip:
    """Load a tip from storage by its ID.

    Args:
        tip_id: The ID of the tip to load

    Returns:
        Tip: The loaded tip

    Raises:
        TipNotFoundError: If the tip with the given ID is not found
    """
    storage_dir = get_storage_dir("tips")

    _, tip_digest = parse_tip_external_id(tip_id)
    tip_path = next(storage_dir.glob(f"*/{tip_digest}.json"), None)

    if tip_path is None:
        raise TipNotFoundError(f"Tip with ID {tip_id} not found")

    try:
        with open(tip_path, "r") as f:
            tip_data = json.load(f)
            tip = Tip.model_validate(tip_data)
            if not tip.deleted or include_deleted:
                return tip

            raise TipNotFoundError(f"Tip with ID {tip_id} not found")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise TipNotFoundError(f"Tip with ID {tip_id} not found") from e


def delete_tip(tip_id: str) -> bool:
    """Logically delete a tip from storage by its ID.

    Args:
        tip_id: The ID of the tip to delete

    Returns:
        bool: True if the tip was deleted, False if the tip was not found
    """
    storage_dir = get_storage_dir("tips")
    _, tip_digest = parse_tip_external_id(tip_id)
    tip_path = next(storage_dir.glob(f"*/{tip_digest}.json"), None)

    if tip_path is None:
        return False

    tip_data = None
    try:
        with open(tip_path, "r") as f:
            tip_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load tip {tip_path}: {e}")
        return False

    tip_data["deleted"] = True

    try:
        with open(tip_path, "w") as f:
            json.dump(tip_data, f, indent=2)
    except (IOError, PermissionError) as e:
        logger.error(f"Failed to save tip {tip_id}: {e}")
        return False

    return True
