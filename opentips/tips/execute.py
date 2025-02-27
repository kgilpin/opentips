import subprocess
from typing import List, Optional


def execute(
    cmd: str, args: List[str], cwd: Optional[str] = None, exitcode: Optional[int] = None
) -> str:
    try:
        result = subprocess.run(
            [cmd] + args, cwd=cwd, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        if exitcode is not None and e.returncode == exitcode:
            return e.stdout
        raise
