from typing import Any, Self
from unittest.mock import Mock, patch

from prff.command import run_command


class MockProcess:
    def __init__(self, *, stdout: bytes = b"", stderr: bytes = b"", returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.patch = patch("prff.command.subprocess.Popen", return_value=self)
        self.mock: Mock | None = None

    def communicate(self) -> tuple[bytes, bytes]:
        return self.stdout, self.stderr

    def __enter__(self) -> Self:
        self.mock = self.patch.start()
        return self

    def __exit__(self, *args: object, **kwargs: Any) -> None:
        self.patch.stop()


def test_run_command():
    with MockProcess(stdout=b"OK") as process:
        result = run_command("echo foo")

    assert result.out == "OK"
    assert result.err is None
    assert result.exit_code == 0

    assert process.mock.call_args.args == (["echo", "foo"],)
    assert process.mock.call_args.kwargs == {"cwd": None, "stderr": -1, "stdout": -1}


def test_run_command__error():
    with MockProcess(stderr=b"Err", returncode=1) as process:
        result = run_command("echo foo")

    assert result.out is None
    assert result.err == "Err"
    assert result.exit_code == 1

    assert process.mock.call_args.args == (["echo", "foo"],)
    assert process.mock.call_args.kwargs == {"cwd": None, "stderr": -1, "stdout": -1}


def test_run_command__directory():
    with MockProcess(stdout=b"OK") as process:
        result = run_command("echo foo", directory="dir")

    assert result.out == "OK"
    assert result.err is None
    assert result.exit_code == 0

    assert process.mock.call_args.args == (["echo", "foo"],)
    assert process.mock.call_args.kwargs == {"cwd": "dir", "stderr": -1, "stdout": -1}
