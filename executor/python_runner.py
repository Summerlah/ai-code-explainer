import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_status: int
    execution_time: float
    timed_out: bool
    error_type: str | None = None
    error_line: int | None = None


def _execution_environment() -> dict[str, str]:
    allowed = ("PATH", "SYSTEMROOT", "WINDIR", "TEMP", "TMP")
    return {name: os.environ[name] for name in allowed if name in os.environ}


def run_python(
    code: str, input_text: str = "", timeout_seconds: float = 3.0
) -> ExecutionResult:
    """Run Python in a separate, time-limited process (not a security sandbox)."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")
    started_at = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="codelab-") as working_directory:
        try:
            process = subprocess.run(
                [sys.executable, "-I", "-c", code],
                input=input_text,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                cwd=Path(working_directory),
                env=_execution_environment(),
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            elapsed = time.perf_counter() - started_at
            stdout = _decode_output(error.stdout)
            stderr = _decode_output(error.stderr)
            return ExecutionResult(
                stdout=stdout,
                stderr=stderr or f"Execution exceeded the {timeout_seconds:g}-second time limit.",
                exit_status=-1,
                execution_time=elapsed,
                timed_out=True,
                error_type="TimeoutError",
            )

    elapsed = time.perf_counter() - started_at
    error_type: str | None = None
    error_line: int | None = None
    if process.returncode != 0:
        match = re.search(r'File "<string>", line (\d+)', process.stderr)
        error_line = int(match.group(1)) if match else None
        error_match = re.search(
            r"(?m)^([A-Za-z_][\w.]*(?:Error|Exception|Interrupt))(?::|$)",
            process.stderr,
        )
        error_type = error_match.group(1) if error_match else "ExecutionError"

    return ExecutionResult(
        stdout=process.stdout,
        stderr=process.stderr,
        exit_status=process.returncode,
        execution_time=elapsed,
        timed_out=False,
        error_type=error_type,
        error_line=error_line,
    )


def _decode_output(output: bytes | str | None) -> str:
    if output is None:
        return ""
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output
