from dataclasses import dataclass
from typing import Literal

from executor.python_runner import run_python


TestStatus = Literal["PASS", "FAIL", "ERROR", "TIMEOUT"]


@dataclass
class TestCaseResult:
    description: str
    expected_output: str
    actual_output: str
    status: TestStatus
    stderr: str
    error_type: str | None
    error_line: int | None
    execution_time: float


def run_test_cases(
    code: str, cases: list[dict[str, str]], timeout_seconds: float = 3.0
) -> list[TestCaseResult]:
    results: list[TestCaseResult] = []
    for case in cases:
        execution = run_python(
            code,
            input_text=case["input"],
            timeout_seconds=timeout_seconds,
        )
        if execution.timed_out:
            status: TestStatus = "TIMEOUT"
        elif execution.exit_status != 0:
            status = "ERROR"
        elif execution.stdout.rstrip("\r\n") == case["expected_output"].rstrip("\r\n"):
            status = "PASS"
        else:
            status = "FAIL"
        results.append(
            TestCaseResult(
                description=case["description"],
                expected_output=case["expected_output"],
                actual_output=execution.stdout.rstrip("\r\n"),
                status=status,
                stderr=execution.stderr,
                error_type=execution.error_type,
                error_line=execution.error_line,
                execution_time=execution.execution_time,
            )
        )
    return results
