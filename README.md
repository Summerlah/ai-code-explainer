# CodeLab AI

CodeLab AI is a GenAI-assisted coding environment that combines Gemini's
explanations and test generation with real Python execution and deterministic
AST-based analysis. Gemini explains and predicts; Python's interpreter is the
source of truth for actual program behavior.

## Features

- Beginner-friendly AI code explanations and walkthroughs
- AI-generated, JSON-validated Python test cases
- Actual Python execution in a separate subprocess with a short timeout
- Automated tests with expected-versus-actual output comparison
- AI vs Reality output prediction and comparison
- Deterministic AST-based code analysis (lines, functions, classes, loops,
  conditions, imports, and detectable variables)
- Runtime error details and Gemini explanations
- Python execution support; Java, C, C++, and JavaScript are listed for
  explanations but are not executed

The subprocess and timeout provide a controlled execution environment for a
college mini-project. They are not a complete security sandbox. Only run code
you trust.

## Setup

1. Create and activate a Python virtual environment (Python 3.10 or newer).
2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and replace the placeholder with your Gemini
   API key from [Google AI Studio](https://aistudio.google.com/apikey). Keep
   `.env` private; it is excluded from Git. The app reads `GEMINI_API_KEY`
   from this file and never displays the key.
4. Start the app:

   ```powershell
   streamlit run app.py
   ```

Paste code, choose its language, and use the available actions:

- **Explain Code** asks Gemini for an overview, concepts, expected input/output,
  possible problems, and a walkthrough.
- **Run Code** executes Python in a separate process. Standard output, standard
  error, exit status, and elapsed time are shown. Execution has a three-second
  timeout.
- **Generate Test Cases** asks Gemini for normal, edge, and boundary test cases.
  The JSON response is validated before it is stored or used.
- **Run Test Cases** executes each generated case and reports PASS, FAIL, ERROR,
  or TIMEOUT.
- **AI vs Reality** shows Gemini's output prediction alongside the actual
  subprocess output.

The **Code Analysis** tab uses Python's built-in AST module; Gemini does not
calculate the structural counts. Gemini requests use the Google `google-genai`
SDK and the `gemini-2.5-flash` model.
