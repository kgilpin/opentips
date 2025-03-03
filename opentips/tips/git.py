from hashlib import sha256
import logging
import os
import subprocess
from typing import List, NamedTuple, Optional

from unidiff import PatchSet
from unidiff.patch import PatchedFile
from charset_normalizer import detect

from .execute import execute

logger = logging.getLogger(__name__)

MAX_PATCH_CHANGES = 250

GIT_COMMANDS = [
    "git",
    "git.exe",
    "c:\\Program Files\\Git\\bin\\git.exe",
]


def detect_git_command() -> str:
    """Detect the git command on the system"""
    for command in GIT_COMMANDS:
        logger.info(f"Checking for git command: {command}")
        try:
            subprocess.run([command, "--version"], stdout=subprocess.DEVNULL)
            logger.info(f"Found git command: {command}")
            return command
        except FileNotFoundError:
            pass
    raise FileNotFoundError("Could not find git command on the system")


class DiffChunk(NamedTuple):
    to_file: str
    chunk: str

    def digest(self) -> str:
        return sha256(self.chunk.encode("utf-8")).hexdigest()


def is_binary_file(file_path: str, chunk_size=1024) -> bool:
    """Check if a file is binary."""
    if os.path.isdir(file_path):
        return False

    with open(file_path, "rb") as f:
        chunk = f.read(chunk_size)
    result = detect(chunk)
    try:
        return result["encoding"] is None
    except KeyError:
        # If 'encoding' key is not present, assume it's binary (for safety)
        logger.warning(f"Could not detect encoding for {file_path}")
        return False


def git_diff(base_branch: str, ignore_list: set[str]) -> List[DiffChunk]:
    # Convert ignore dirs to Git pathspec exclusions (e.g., ":!dir1" ":!dir2")
    exclude_paths = []
    for file_or_dir in ignore_list:
        if not os.path.exists(file_or_dir):
            continue
        exclude_paths.append(f":!{file_or_dir}")

    # List files that have a diff in the project so that we can exclude binary files.
    # We could consider using --name-status, but --name-only is sufficient for now.
    git_command = detect_git_command()
    args = ["diff", "--diff-filter=ACM", "--name-only", base_branch] + exclude_paths
    try:
        diff_files = execute(git_command, args, exitcode=1).strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing git diff: {e}")
        return []

    # Expand the exclude paths to include binary files
    binary_files = [file for file in diff_files.splitlines() if is_binary_file(file)]
    logger.debug("Excluding binary files: %r", binary_files)
    exclude_paths += [f":!{file}" for file in binary_files]

    # Combine the base command with exclusion paths
    args = [
        "diff",
        "--diff-filter=ACM",
        "--function-context",
        base_branch,
    ] + exclude_paths
    try:
        diff_output = execute(git_command, args, exitcode=1)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing git diff: {e}")
        return []

    # This is defined as a multi-line function so that we can include the logging.
    def is_large_patch(patch: PatchedFile) -> bool:
        """
        Compute the number of changed lines in the patch and discard it if it's too large.
        """
        changed_lines = patch.added + patch.removed
        if changed_lines > MAX_PATCH_CHANGES:
            logger.debug(f"Skipping large diff with {changed_lines} changed lines")
            return True

        return False

    diffs = []
    if diff_output:
        diffs.extend(
            DiffChunk(to_file=patch.path, chunk=str(patch))
            for patch in PatchSet(diff_output)
            if not is_large_patch(patch)
        )

    # Get untracked files
    untracked_output = execute(git_command, ["status", "--porcelain"]).strip()

    # Filter out untracked files (lines starting with "??")
    untracked_files = (
        line[3:] for line in untracked_output.splitlines() if line.startswith("??")
    )

    def is_ignored_dir(path: str) -> bool:
        return any(path.startswith(ignore_dir) for ignore_dir in ignore_list)

    # Process untracked files
    for line in untracked_files:
        if not line or is_ignored_dir(line) or line.startswith("__debug"):
            logger.debug(f"Skipping untracked ignored file: {line}")
            continue

        if is_binary_file(line):
            logger.warning(f"Skipping binary file: {line}")
            continue

        if os.path.isdir(line):
            logger.debug(f"Skipping untracked directory: {line}")
            continue

        try:
            with open(line, "r", encoding="utf-8") as f:
                file_contents = f.read()
        except UnicodeDecodeError:
            logger.warning(f"Skipping file due to encoding issues: {line}")
            continue
        except IOError as e:
            logger.error(f"Error reading file contents for {line}: {e}")
            continue

        if not file_contents:
            continue

        # Format file contents as git diff
        diff_lines = [f"+{line}" for line in file_contents.splitlines()]
        diff_output = f"diff --git a/{line} b/{line}\n" + "\n".join(diff_lines)
        diffs.append(DiffChunk(to_file=line, chunk=diff_output))

    return diffs


def git_detect_branch_in_history(branches: List[str]) -> Optional[str]:
    git_command = detect_git_command()
    try:
        output = execute(git_command, ["branch", "--list", "--format=%(refname:short)"])
        named_branch_history = [line for line in output.splitlines() if line]

        for base_branch in branches:
            if base_branch in named_branch_history:
                return base_branch

        return None
    except subprocess.CalledProcessError:
        return None
