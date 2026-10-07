from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from ai.gemini import (
    GeminiError,
    explain_code,
    explain_runtime_error,
    generate_test_cases,
    predict_output,
)
from analyzer.code_analyzer import analyze_python_code
from executor.python_runner import ExecutionResult, run_python
from tests.test_runner import run_test_cases


LANGUAGES = ["Python", "Java", "C", "C++", "JavaScript"]

load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(page_title="CodeLab AI", page_icon="🧪", layout="wide")
st.title("CodeLab AI")
st.subheader("Understand • Run • Test • Analyze")
st.caption(
    "A GenAI-assisted coding workspace. Gemini explains and predicts; Python's "
    "interpreter provides actual execution results."
)

language = st.selectbox("Programming language", LANGUAGES)
code = st.text_area(
    "Your code",
    height=300,
    placeholder="Paste your code here...",
    key="source_code",
)

st.caption(
    "Python execution uses a separate process with a short timeout. This is a "
    "controlled execution environment, not a completely secure sandbox."
)
action_columns = st.columns(4)
run_clicked = action_columns[0].button("Run Code", type="primary", use_container_width=True)
explain_clicked = action_columns[1].button("Explain Code", use_container_width=True)
generate_clicked = action_columns[2].button(
    "Generate Test Cases", use_container_width=True
)
tests_clicked = action_columns[3].button(
    "Run Test Cases", use_container_width=True
)

for state_key, default in (
    ("explanation", ""),
    ("test_cases", []),
    ("test_results", []),
    ("execution_result", None),
    ("runtime_explanation", ""),
    ("runtime_explanation_error", ""),
    ("test_error_explanation", ""),
    ("test_error_explanation_error", ""),
    ("ai_prediction", None),
):
    st.session_state.setdefault(state_key, default)

source_signature = (language, code)
previous_signature = st.session_state.get("_source_signature")
if previous_signature is not None and previous_signature != source_signature:
    for state_key, reset_value in (
        ("explanation", ""),
        ("test_cases", []),
        ("test_results", []),
        ("execution_result", None),
        ("runtime_explanation", ""),
        ("runtime_explanation_error", ""),
        ("test_error_explanation", ""),
        ("test_error_explanation_error", ""),
        ("ai_prediction", None),
    ):
        st.session_state[state_key] = reset_value
st.session_state["_source_signature"] = source_signature


def _show_gemini_error(error: GeminiError) -> None:
    st.error(str(error))


def _request_runtime_explanation(
    source: str, result: ExecutionResult
) -> tuple[str, str]:
    if not result.error_type or result.timed_out:
        return "", ""
    details = result.stderr.strip().splitlines()
    message = details[-1] if details else "The program exited with an error."
    try:
        with st.spinner("Asking Gemini to explain the runtime error..."):
            return (
                explain_runtime_error(
                    source,
                    result.error_type,
                    message,
                    result.error_line,
                ),
                "",
            )
    except GeminiError as error:
        return "", str(error)


if run_clicked:
    if not code.strip():
        st.error("Please enter some code before running it.")
    elif language != "Python":
        st.warning(
            f"Execution is currently supported only for Python. "
            f"{language} code is not executed."
        )
    else:
        with st.spinner("Running Python in a separate process..."):
            result = run_python(code)
        st.session_state.execution_result = result
        st.session_state.runtime_explanation = ""
        st.session_state.runtime_explanation_error = ""
        (
            st.session_state.runtime_explanation,
            st.session_state.runtime_explanation_error,
        ) = _request_runtime_explanation(code, result)

if explain_clicked:
    if not code.strip():
        st.error("Please enter some code before asking for an explanation.")
    else:
        try:
            with st.spinner("Gemini is analyzing your code..."):
                st.session_state.explanation = explain_code(code, language)
        except GeminiError as error:
            st.session_state.explanation = ""
            _show_gemini_error(error)

if generate_clicked:
    if not code.strip():
        st.error("Please enter some code before generating test cases.")
    elif language != "Python":
        st.warning(
            "AI-generated executable test cases are currently supported only for Python."
        )
    else:
        try:
            with st.spinner("Gemini is generating and validating test cases..."):
                st.session_state.test_cases = generate_test_cases(code)
            st.session_state.test_results = []
        except GeminiError as error:
            st.session_state.test_cases = []
            _show_gemini_error(error)

if tests_clicked:
    if language != "Python":
        st.warning("Test execution is currently supported only for Python.")
    elif not code.strip():
        st.error("Please enter Python code before running test cases.")
    elif not st.session_state.test_cases:
        st.error("Generate test cases first, then run them.")
    else:
        with st.spinner("Running each test case in a separate Python process..."):
            results = run_test_cases(code, st.session_state.test_cases)
        st.session_state.test_results = results
        st.session_state.test_error_explanation = ""
        st.session_state.test_error_explanation_error = ""
        error_result = next(
            (
                result
                for result in results
                if result.status == "ERROR" and result.error_type
            ),
            None,
        )
        if error_result is not None:
            details = error_result.stderr.strip().splitlines()
            message = details[-1] if details else "The program exited with an error."
            try:
                with st.spinner("Asking Gemini to explain a test execution error..."):
                    st.session_state.test_error_explanation = explain_runtime_error(
                        code,
                        error_result.error_type or "ExecutionError",
                        message,
                        error_result.error_line,
                    )
            except GeminiError as error:
                st.session_state.test_error_explanation_error = str(error)

tabs = st.tabs(
    [
        "AI Explanation",
        "Code Analysis",
        "Test Cases",
        "Execution",
        "AI vs Reality",
    ]
)

with tabs[0]:
    st.markdown("### AI Code Explanation")
    if st.session_state.explanation:
        st.markdown(st.session_state.explanation)
    else:
        st.info("Select **Explain Code** to get a beginner-friendly walkthrough.")

with tabs[1]:
    st.markdown("### Deterministic Python Code Analysis")
    if language != "Python":
        st.info("AST-based analysis is currently available for Python code.")
    elif not code.strip():
        st.info("Enter Python code to see its structure.")
    else:
        try:
            metrics = analyze_python_code(code)
        except SyntaxError as error:
            st.error(
                f"Python syntax error on line {error.lineno or 'unknown'}: "
                f"{error.msg}"
            )
        else:
            metric_columns = st.columns(4)
            for index, (label, value) in enumerate(metrics.items()):
                metric_columns[index % len(metric_columns)].metric(
                    label.replace("_", " ").title(), value
                )
            st.caption(
                "Variable count is the number of distinct assigned names and "
                "function/lambda parameters detected by the AST."
            )

with tabs[2]:
    st.markdown("### Generated Test Cases")
    if st.session_state.test_cases:
        st.dataframe(
            st.session_state.test_cases,
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("Generate test cases to review the AI-proposed inputs and outputs.")

    if st.session_state.test_results:
        st.markdown("### Test Results")
        st.dataframe(
            [
                {
                    "Test Case": result.description,
                    "Expected": result.expected_output,
                    "Actual": result.actual_output,
                    "Result": result.status,
                    "Time (s)": round(result.execution_time, 4),
                }
                for result in st.session_state.test_results
            ],
            hide_index=True,
            use_container_width=True,
        )
        for result in st.session_state.test_results:
            if result.status in ("ERROR", "TIMEOUT"):
                with st.expander(f"{result.status}: {result.description}"):
                    if result.error_type:
                        st.write(f"Error type: {result.error_type}")
                    if result.error_line is not None:
                        st.write(f"Line: {result.error_line}")
                    if result.stderr:
                        st.code(result.stderr, language="text")
        if st.session_state.test_error_explanation:
            st.markdown("#### Gemini's error explanation")
            st.markdown(st.session_state.test_error_explanation)
        elif st.session_state.test_error_explanation_error:
            st.error(st.session_state.test_error_explanation_error)

with tabs[3]:
    st.markdown("### Python Execution")
    result = st.session_state.execution_result
    if result is None:
        st.info("Select **Run Code** to execute Python and inspect its output.")
    else:
        status = "TIMEOUT" if result.timed_out else (
            "ERROR" if result.exit_status != 0 else "COMPLETED"
        )
        st.write(f"**Status:** {status}")
        st.write(f"**Exit status:** {result.exit_status}")
        st.write(f"**Execution time:** {result.execution_time:.4f} seconds")
        st.markdown("**stdout**")
        st.code(result.stdout or "(no output)", language="text")
        if result.stderr:
            st.markdown("**stderr**")
            st.code(result.stderr, language="text")
        if result.error_type:
            st.write(f"**Error type:** {result.error_type}")
        if result.error_line is not None:
            st.write(f"**Line:** {result.error_line}")
        if st.session_state.runtime_explanation:
            st.markdown("#### Gemini's beginner-friendly error explanation")
            st.markdown(st.session_state.runtime_explanation)
        elif st.session_state.runtime_explanation_error:
            st.error(st.session_state.runtime_explanation_error)

with tabs[4]:
    st.markdown("### AI vs Reality")
    st.write(
        "Gemini makes a prediction first. The separate Python process then runs "
        "the code; its output is the source of truth."
    )
    if language != "Python":
        st.info("AI vs Reality execution is currently supported only for Python.")
    else:
        prediction_input = st.text_area(
            "Input sent to the program",
            key="prediction_input",
            placeholder="Enter stdin text here...",
        )
        if st.button("Compare AI Prediction with Execution"):
            if not code.strip():
                st.error("Please enter Python code before comparing outputs.")
            else:
                try:
                    with st.spinner("Gemini is predicting the output..."):
                        prediction = predict_output(code, prediction_input)
                    with st.spinner("Running the Python program..."):
                        actual = run_python(code, prediction_input)
                    st.session_state.ai_prediction = {
                        "prediction": prediction,
                        "execution": actual,
                    }
                except GeminiError as error:
                    st.session_state.ai_prediction = None
                    _show_gemini_error(error)

        comparison = st.session_state.ai_prediction
        if comparison is not None:
            actual = comparison["execution"]
            if actual.timed_out:
                comparison_status = "EXECUTION TIMEOUT"
            elif actual.exit_status != 0:
                comparison_status = "EXECUTION ERROR"
            elif comparison["prediction"].rstrip("\r\n") == actual.stdout.rstrip("\r\n"):
                comparison_status = "MATCH"
            else:
                comparison_status = "MISMATCH"
            result_columns = st.columns(3)
            result_columns[0].markdown("**AI Prediction**")
            result_columns[0].code(comparison["prediction"] or "(no output)", language="text")
            result_columns[1].markdown("**Actual Output**")
            result_columns[1].code(actual.stdout or "(no output)", language="text")
            result_columns[2].markdown("**Status**")
            result_columns[2].subheader(comparison_status)
            if actual.stderr:
                st.markdown("**Actual stderr**")
                st.code(actual.stderr, language="text")
