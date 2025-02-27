from typing import Optional

from .storage import is_diff_chunk_new
from .git import DiffChunk, git_detect_branch_in_history, git_diff

BASE_BRANCHES = [
    "main",
    "master",
    "develop",
]

IGNORE_LIST = {
    "node_modules",
    "vendor",
    "venv",
    "dist",
    "build",
    "target",
    "coverage",
    "tmp",
    "log",
    "venv",
    ".venv",
    "yarn.lock",
    "package-lock.json",
    "Gemfile.lock",
    "go.sum",
    "composer.lock",
}


def diff(new_only: Optional[bool] = False) -> Optional[list[DiffChunk]]:
    base_branch = git_detect_branch_in_history(BASE_BRANCHES)
    if not base_branch:
        return None

    ignore_list = IGNORE_LIST

    diff_chunks = git_diff(base_branch, ignore_list)
    if new_only:
        diff_chunks = list(filter(lambda x: is_diff_chunk_new(x), diff_chunks))

    return diff_chunks
