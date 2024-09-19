import subprocess
from pathlib import Path


def run_command(command: str, *, directory: Path | None = None) -> str | None:
    """
    Run a command in the given directory using subprocess.
    Return the stdout of the command if it succeeds, otherwise return None and log the error.

    :param command: The command string to run.
    :param directory: The directory to run the command in.
    """
    process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)
    stdout, stderr = process.communicate()

    error = stderr.decode()
    if error:
        print(error)
        return None

    return stdout.decode().strip()


def get_exit_code(command: str, *, directory: Path | None = None) -> int:
    """
    Run a command in the given directory using subprocess.
    Return the exit code of the command.

    :param command: The command string to run.
    :param directory: The directory to run the command in.
    """
    process = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=directory)
    process.communicate()
    return process.returncode
