import os
import unittest
from unittest.mock import Mock, patch

import httpx
from google.genai import errors

from ai.gemini import GeminiError, _client, _generate, generate_test_cases


class GeminiTestCaseValidationTests(unittest.TestCase):
    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    def test_reports_missing_api_key(self) -> None:
        with self.assertRaisesRegex(GeminiError, "API key is missing"):
            _client()

    @patch.dict(os.environ, {"GEMINI_API_KEY": ""})
    @patch("ai.gemini._streamlit_api_key", return_value="cloud-secret")
    @patch("ai.gemini.genai.Client")
    def test_reads_api_key_from_streamlit_cloud_secrets(
        self, make_client: Mock, read_secret: Mock
    ) -> None:
        _client()

        make_client.assert_called_once()
        self.assertEqual(make_client.call_args.kwargs["api_key"], "cloud-secret")
        read_secret.assert_called_once_with()

    @patch("ai.gemini._generate")
    def test_accepts_valid_json_test_cases(self, generate: Mock) -> None:
        generate.return_value = (
            '[{"description":"Normal input","input":"4\\n",'
            '"expected_output":"True"}]'
        )

        cases = generate_test_cases("print(int(input()) % 2 == 0)")

        self.assertEqual(cases[0]["description"], "Normal input")
        self.assertEqual(cases[0]["input"], "4\n")
        self.assertEqual(cases[0]["expected_output"], "True")

    @patch("ai.gemini._generate")
    def test_rejects_malformed_json_without_crashing(self, generate: Mock) -> None:
        generate.return_value = "not JSON"

        with self.assertRaisesRegex(GeminiError, "malformed"):
            generate_test_cases("print('hello')")

    @patch("ai.gemini._generate")
    def test_rejects_unexpected_case_fields(self, generate: Mock) -> None:
        generate.return_value = (
            '[{"description":"Case","input":"","expected_output":"ok",'
            '"command":"do not run"}]'
        )

        with self.assertRaisesRegex(GeminiError, "invalid test case"):
            generate_test_cases("print('ok')")

    @patch("ai.gemini._client")
    def test_handles_empty_responses(self, make_client: Mock) -> None:
        client = Mock()
        client.models.generate_content.return_value.text = " "
        make_client.return_value = client

        with self.assertRaisesRegex(GeminiError, "empty response"):
            _generate("prompt")

    @patch("ai.gemini._client")
    def test_requests_structured_json_response(self, make_client: Mock) -> None:
        client = Mock()
        client.models.generate_content.return_value.text = "[]"
        make_client.return_value = client

        self.assertEqual(_generate("prompt", json_response=True), "[]")
        config = client.models.generate_content.call_args.kwargs["config"]
        self.assertEqual(config.response_mime_type, "application/json")

    @patch("ai.gemini._client")
    def test_handles_rate_limits(self, make_client: Mock) -> None:
        make_client.side_effect = errors.APIError(
            code=429,
            response_json={"error": {"message": "quota reached"}},
        )

        with self.assertRaisesRegex(GeminiError, "rate or usage limits"):
            _generate("prompt")

    @patch("ai.gemini._client")
    def test_handles_request_timeouts(self, make_client: Mock) -> None:
        make_client.side_effect = httpx.ReadTimeout("request timed out")

        with self.assertRaisesRegex(GeminiError, "timed out"):
            _generate("prompt")


if __name__ == "__main__":
    unittest.main()
