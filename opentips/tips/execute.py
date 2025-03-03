import subprocess
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def execute(
    cmd: str, args: List[str], cwd: Optional[str] = None, exitcode: Optional[int] = None
) -> str:
    cmd_plus_args = [cmd] + args
    logger.debug(f"Executing: {' '.join(cmd_plus_args)}")
    try:
        result = subprocess.run(
            cmd_plus_args, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        if exitcode is not None and e.returncode == exitcode:
            return e.stdout

        logger.info(
            f"Command failed with exit code {e.returncode}: {' '.join(cmd_plus_args)}"
        )
        raise
