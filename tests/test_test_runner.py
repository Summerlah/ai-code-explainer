import unittest

from tests.test_runner import run_test_cases


class TestCaseRunnerTests(unittest.TestCase):
    def test_compares_actual_output_to_expected_output(self) -> None:
        cases = [
            {
                "description": "correct result",
                "input": "5\n",
                "expected_output": "25",
            },
            {
                "description": "incorrect expectation",
                "input": "5\n",
                "expected_output": "26",
            },
            {
                "description": "significant spaces differ",
                "input": "\n",
                "expected_output": " 25",
            },
        ]

        results = run_test_cases(
            "value = input()\nprint(int(value) ** 2) if value else print('25')",
            cases,
        )

        self.assertEqual(
            [result.status for result in results], ["PASS", "FAIL", "FAIL"]
        )
        self.assertEqual(results[0].actual_output, "25")

    def test_marks_errors_and_timeouts(self) -> None:
        cases = [
            {"description": "error", "input": "", "expected_output": ""},
            {"description": "timeout", "input": "", "expected_output": ""},
        ]

        results = run_test_cases(
            "raise ValueError('bad')\n# input",
            cases[:1],
        )
        timeout_result = run_test_cases(
            "while True:\n    pass",
            cases[1:],
            timeout_seconds=0.1,
        )

        self.assertEqual(results[0].status, "ERROR")
        self.assertEqual(timeout_result[0].status, "TIMEOUT")


if __name__ == "__main__":
    unittest.main()
