import unittest

from executor.python_runner import run_python


class PythonRunnerTests(unittest.TestCase):
    def test_captures_output_and_accepts_input(self) -> None:
        result = run_python("name = input()\nprint('Hello', name)", "Ada\n")

        self.assertEqual(result.stdout, "Hello Ada\n")
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.exit_status, 0)
        self.assertFalse(result.timed_out)

    def test_captures_runtime_error_and_line(self) -> None:
        result = run_python("values = []\nprint(values[0])")

        self.assertEqual(result.error_type, "IndexError")
        self.assertEqual(result.error_line, 2)
        self.assertNotEqual(result.exit_status, 0)

    def test_times_out_long_running_code(self) -> None:
        result = run_python("while True:\n    pass", timeout_seconds=0.1)

        self.assertTrue(result.timed_out)
        self.assertEqual(result.error_type, "TimeoutError")


if __name__ == "__main__":
    unittest.main()
