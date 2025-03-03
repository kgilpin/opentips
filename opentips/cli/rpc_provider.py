import asyncio
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

from opentips.comm.message_completion import (
    complete_response,
)
from opentips.tips.diff import diff
from opentips.tips.invalidate_tips import invalidate_tips
from opentips.tips.prune_tips import prune_tips
from opentips.tips.git import detect_git_command

from ..tips.explain_tip import explain_tip as explain_tip_fn
from ..tips.fetch_tips import (
    fetch_tips_for_diff,
    fetch_tips_for_file_range,
)
from ..tips.storage import (
    load_tip,
    list_tips as list_tips_fn,
    delete_tip as delete_tip_fn,
)
from ..tips.event_broadcaster import event_broadcaster
from ..tips.tips_job import TipsJob
from .apply_tip_job import ApplyTipJob
from ..tips.rpc_types import (
    ChangedResponse,
    OpenTipsRPC,
    PatchResponse,
    Tip,
    TipList,
    ExplanationResponse,
)

logger = logging.getLogger(__name__)

EXCLUDE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".bzr",
    "__pycache__",
    ".tox",
    ".venv",
    "venv",
    ".vscode",
    ".vscode-test",
    ".idea",
    ".pytest_cache",
    "node_modules",
    "build",
    "dist",
    "target",
    ".aider.tags.cache.v3",
}


def filter_git_ignored(file_names: list[str]) -> list[str]:
    """
    Filter out file names that are ignored by git
    """

    def includes_excluded_dir(file_name: str) -> bool:
        return any(part in EXCLUDE_DIRS for part in Path(file_name).parts)

    file_names = [
        file_name for file_name in file_names if not includes_excluded_dir(file_name)
    ]

    git_command = detect_git_command()
    result = []
    for file_names_batch in [
        file_names[i : i + 100] for i in range(0, len(file_names), 100)
    ]:
        cmd_plus_args = [git_command, "check-ignore"] + file_names_batch
        process = subprocess.run(cmd_plus_args)
        if process.returncode == 0:
            logger.debug(f"[rpc-provider] Some of the files are ignored")
            # Some files are ignored, check them individually
            for file_name in file_names_batch:
                cmd_plus_args = [git_command, "check-ignore", file_name]
                individual_process = subprocess.run(cmd_plus_args)
                if individual_process.returncode == 1:
                    # The file is not ignored
                    logger.debug(f"[rpc-provider] File {file_name} is not ignored")
                    result.append(file_name)
                elif individual_process.returncode == 0:
                    logger.debug(f"[rpc-provider] File {file_name} is ignored")
                elif individual_process.returncode != 0:
                    logger.error(
                        f"[rpc-provider] Error running git check-ignore on {file_name}: {individual_process.stderr}"
                    )
                    result.append(file_name)
        elif process.returncode == 1:
            # None of the files are ignored
            logger.debug(f"[rpc-provider] None of the files are ignored")
            result.extend(file_names_batch)
        else:
            logger.error(
                f"[rpc-provider] Error running git check-ignore: {process.stderr}"
            )
            result.extend(file_names_batch)

    return result


class RPCProvider(OpenTipsRPC):
    """
    Implements the OpenTipsRPC protocol

    Args:
    tip_delay (float): The delay in seconds before responding to file changes.
        If additional changes occur within this time frame, the delay is reset.
        Once the delay has passed without additional changes, the tip request is processed.
    """

    def __init__(self, *, tip_delay: int, tips_limit: int) -> None:
        self.directory = os.getcwd()
        self.tip_request = TipsJob(delay=tip_delay, tips_limit=tips_limit)
        self.tips_limit = tips_limit

    def echo(self, message: str) -> str:
        """Test method that echoes back the message"""
        event_broadcaster.enqueue_event("echo", {"message": message})
        return message

    def poll_events(self) -> List[Dict[str, Any]]:
        return event_broadcaster.poll_events()

    def changed(
        self, file_names: list[str], immediate: Optional[bool] = False
    ) -> ChangedResponse:
        """Handle notification of changed files"""
        logger.info("[rpc-provider] Changed files: %s", ", ".join(file_names))
        included_file_names = filter_git_ignored(file_names)
        if not included_file_names:
            logger.info("[rpc-provider] No files need to be analyzed")
            return ChangedResponse(file_names=[])

        logger.info(
            "[rpc-provider] Files to be analyzed: %s", ", ".join(included_file_names)
        )
        if immediate:
            asyncio.create_task(self.tip_request.process_tips())
        else:
            self.tip_request.schedule()
        return ChangedResponse(file_names=included_file_names)

    async def suggest(self, new_only: Optional[bool]) -> TipList:
        """Get suggestions for changed files"""
        if new_only is None:
            new_only = True
        diff_chunks = diff(new_only=new_only)
        if not diff_chunks:
            logger.debug("[rpc-provider] No diff content to analyze")
            return TipList(tips=[])

        tip_list = await fetch_tips_for_diff(diff_chunks)
        event_broadcaster.enqueue_event("tips", tip_list.model_dump())
        return tip_list

    def complete_response(self, request_id: str, response: Any) -> Any:
        logger.info(
            "[rpc-provider] Received response for message %s: %r", request_id, response
        )

        complete_response(request_id, response)

    async def suggest_file_range(
        self, file_name: str, start_line: int, end_line: int
    ) -> TipList:
        """Get suggestions for a specific line range in a file

        Args:
            file_name: Path to the file to analyze
            start_line: Starting line number (1-based)
            end_line: Ending line number (1-based, inclusive)

        Returns:
            TipList containing suggestions for the specified range
        """
        tip_list = await fetch_tips_for_file_range(
            file_name=file_name, start_line=start_line, end_line=end_line
        )

        event_broadcaster.enqueue_event("tips", tip_list.model_dump())
        return tip_list

    async def list_tips(self, limit: Optional[int] = None) -> List[Tip]:
        """
        List all tips in the current working directory, ensuring that the tips are
        still valid based on the current file content.
        """
        if not limit:
            limit = self.tips_limit

        tips = list_tips_fn()
        tips = invalidate_tips(tips)
        tips = await prune_tips(tips, limit)

        return tips

    async def fetch_tip(self, tip_id: str) -> Tip:
        """Fetch a specific tip"""
        Tip.validate_external_id(tip_id, self.directory)
        return load_tip(tip_id)

    async def explain_tip(self, tip_id: str) -> ExplanationResponse:
        """Get explanation for a tip"""
        Tip.validate_external_id(tip_id, self.directory)
        tip = load_tip(tip_id)
        explanation = await explain_tip_fn(tip)
        return ExplanationResponse(explanation=explanation)

    # TODO: add dry_run parameter which is implemented by apply_tip_job.py
    async def apply_tip(
        self, tip_id: str, delete_after_apply: bool = False
    ) -> PatchResponse:
        """
        Apply a tip and optionally delete it after successful application.

        Args:
            tip_id: The ID of the tip to apply.
            delete_after_apply: If True, delete the tip after successful application.

        Returns:
            PatchResponse: The result of applying the tip.
        """
        Tip.validate_external_id(tip_id, self.directory)
        tip = load_tip(tip_id)
        apply_tip = ApplyTipJob(tip)
        patches = await apply_tip.apply(delete_after_apply=delete_after_apply)

        if not patches:
            return PatchResponse(success=False, patches=[])

        return PatchResponse(success=True, patches=patches)

    async def delete_tip(self, tip_id: str) -> bool:
        """Delete a tip"""
        Tip.validate_external_id(tip_id, self.directory)
        deleted = delete_tip_fn(tip_id)
        if deleted:
            event_broadcaster.enqueue_event(
                "tip_deleted", {"tip_id": tip_id, "reason": "deleted"}
            )

        return deleted
