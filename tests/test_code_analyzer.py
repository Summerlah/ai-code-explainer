import unittest

from analyzer.code_analyzer import analyze_python_code


class CodeAnalyzerTests(unittest.TestCase):
    def test_counts_basic_python_constructs(self) -> None:
        code = (
            "import math\n"
            "class Calculator:\n"
            "    def double(self, value):\n"
            "        result = value * 2\n"
            "        if result > 0:\n"
            "            for item in range(result):\n"
            "                print(item)\n"
        )

        self.assertEqual(
            analyze_python_code(code),
            {
                "lines": 7,
                "functions": 1,
                "classes": 1,
                "loops": 1,
                "conditions": 1,
                "imports": 1,
                "variables": 4,
            },
        )

    def test_reports_syntax_errors(self) -> None:
        with self.assertRaises(SyntaxError):
            analyze_python_code("if True print('missing colon')")


if __name__ == "__main__":
    unittest.main()
