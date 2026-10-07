import json
import os
from typing import Any

import httpx
import streamlit as st
from google import genai
from google.genai import errors, types


MODEL = "gemini-2.5-flash"
REQUEST_TIMEOUT_MS = 30_000


class GeminiError(Exception):
    """An actionable error returned while using the Gemini API."""


def _streamlit_api_key() -> str:
    try:
        return str(st.secrets.get("GEMINI_API_KEY", "")).strip()
    except st.errors.StreamlitSecretNotFoundError:
        return ""


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip() or _streamlit_api_key()
    if not api_key:
        raise GeminiError(
            "The Gemini API key is missing. Set GEMINI_API_KEY in your .env file "
            "for local use or in Streamlit Cloud's Secrets settings."
        )
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS),
    )


def _generate(prompt: str, *, json_response: bool = False) -> str:
    config = (
        types.GenerateContentConfig(response_mime_type="application/json")
        if json_response
        else None
    )
    try:
        response = _client().models.generate_content(
            model=MODEL,
            contents=prompt,
            config=config,
        )
    except errors.APIError as error:
        status = getattr(error, "code", None)
        if status in (401, 403):
            message = "Gemini rejected the API key or its permissions. Check your Google AI access."
        elif status == 429:
            message = "Gemini rate or usage limits were reached. Wait and try again."
        elif status in (503, 504):
            message = "Gemini is temporarily unavailable. Please try again shortly."
        else:
            message = f"Gemini returned an API error (HTTP {status}). Please try again."
        raise GeminiError(message) from error
    except (
        httpx.TimeoutException,
        httpx.NetworkError,
        TimeoutError,
        ConnectionError,
    ) as error:
        raise GeminiError("The Gemini request timed out or could not connect. Please try again.") from error

    text = response.text
    if not text or not text.strip():
        raise GeminiError("Gemini returned an empty response. Please try again.")
    return text.strip()


def explain_code(code: str, language: str) -> str:
    prompt = (
        "You are an expert programming tutor. Explain this source code to a beginner. "
        "Cover what it does, how it works, important programming concepts, expected "
        "input/output, and potential problems. Use clear headings and a section-by-section "
        "walkthrough, or line-by-line for short programs.\n\n"
        f"Programming language: {language}\nSource code:\n```{language.lower()}\n{code}\n```"
    )
    return _generate(prompt)


def generate_test_cases(code: str) -> list[dict[str, str]]:
    prompt = (
        "Generate 3 to 6 useful test cases for the Python program below. Include normal, "
        "edge, and boundary cases where appropriate. Do not execute the program. "
        'Return only a JSON array. Each item must have exactly these string fields: '
        '"description", "input", and "expected_output". The input is text sent to stdin; '
        "expected_output is the exact expected stdout (without a trailing newline).\n\n"
        f"Python code:\n```python\n{code}\n```"
    )
    response = _generate(prompt, json_response=True)
    try:
        data: Any = json.loads(response)
    except json.JSONDecodeError as error:
        raise GeminiError(
            "Gemini returned malformed test-case JSON. Please retry generation."
        ) from error

    if not isinstance(data, list) or not data or len(data) > 20:
        raise GeminiError("Gemini returned an invalid test-case list. Please retry.")

    validated: list[dict[str, str]] = []
    required_fields = {"description", "input", "expected_output"}
    for case in data:
        if (
            not isinstance(case, dict)
            or set(case) != required_fields
            or not all(isinstance(case[field], str) for field in required_fields)
            or not case["description"].strip()
        ):
            raise GeminiError(
                "Gemini returned an invalid test case. Please retry generation."
            )
        validated.append(
            {
                "description": case["description"].strip(),
                "input": case["input"],
                "expected_output": case["expected_output"],
            }
        )
    return validated


def predict_output(code: str, input_text: str) -> str:
    prompt = (
        "Predict the stdout produced by running this Python program with the given stdin. "
        "Do not execute it. Return only the predicted stdout, without explanation or "
        "surrounding quotes. If it raises an error, state the likely exception briefly.\n\n"
        f"stdin:\n{input_text}\n\nPython code:\n```python\n{code}\n```"
    )
    return _generate(prompt)


def explain_runtime_error(
    code: str, error_type: str, error_message: str, line_number: int | None
) -> str:
    location = f" at line {line_number}" if line_number is not None else ""
    prompt = (
        "Explain this Python runtime error to a beginner. Describe what happened, why "
        "the code caused it, and a practical way to fix it. Do not claim to run the code.\n\n"
        f"Error: {error_type}{location}: {error_message}\n"
        f"Python code:\n```python\n{code}\n```"
    )
    return _generate(prompt)
