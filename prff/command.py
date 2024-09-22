from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "run_command",
]


@dataclass
class CommandResult:
    out: str | None
    err: str | None
    exit_code: int


def run_command(command: str, *, directory: Path | str | None = None) -> CommandResult | None:
    """
    Run a command in the given directory using subprocess.

    :param command: The command string to run.
    :param directory: The directory to run the command in.
    """
    process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)
    stdout, stderr = process.communicate()

    error = stderr.decode().strip() or None
    result = stdout.decode().strip() if not error else None

    return CommandResult(out=result, err=error, exit_code=process.returncode)
