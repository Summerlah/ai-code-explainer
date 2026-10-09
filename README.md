# CodeLab AI

CodeLab AI is a GenAI-assisted coding environment that combines Gemini's explanations and test generation with real Python execution and AST-based code analysis. Gemini explains and predicts, while Python's interpreter determines actual program behavior.

## 🚀 Live Demo

**[Open CodeLab AI](https://ai-code-explainer-ejnjpajhlkstt7ywq6tqtf.streamlit.app/)**

Try AI-powered code explanations, automatic test-case generation, Python execution, code analysis, and AI vs Reality comparisons.

## ✨ Features

- **AI Code Explanation:** Beginner-friendly explanations and code walkthroughs.
- **AI Test Case Generation:** Automatically generates test cases for normal, edge, and boundary scenarios.
- **Python Execution:** Runs Python code in a separate subprocess with a three-second timeout.
- **Automated Testing:** Compares expected and actual outputs with PASS, FAIL, ERROR, or TIMEOUT results.
- **AI vs Reality:** Compares Gemini's predicted output with actual Python execution.
- **AST-Based Code Analysis:** Identifies functions, classes, loops, conditions, imports, and other code structures.
- **Error Explanation:** Displays runtime errors and provides AI-generated explanations.
- **Multiple Language Explanations:** Supports explanations for Python, Java, C, C++, and JavaScript. Code execution is currently supported only for Python.

> **Note:** The subprocess and timeout do not provide a complete security sandbox. Only run code you trust.

## 🛠️ Tech Stack

- Python
- Streamlit
- Google Gemini API
- `google-genai`
- Python AST
- Subprocess
- `python-dotenv`

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Summerlah/ai-code-explainer.git
cd ai-code-explainer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Get an API key from [Google AI Studio](https://aistudio.google.com/apikey).

Create a `.env` file and add:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

Never upload your actual API key or `.env` file to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

## 🔄 How It Works

1. **Enter Code:** Paste your source code into the application.
2. **Analyze:** Inspect the program structure using Python's AST module.
3. **Explain:** Gemini explains the code and its programming concepts.
4. **Generate Tests:** Generate and validate test cases in JSON format.
5. **Execute:** Run Python code and capture output, errors, and execution status.
6. **Compare:** Compare expected results with actual results and review AI predictions.

## 💡 What Makes CodeLab AI Different?

Traditional code explainers primarily explain source code. CodeLab AI combines GenAI with actual execution, automated testing, and deterministic code analysis.

Its **AI vs Reality** feature compares an AI-generated prediction with the result produced by executing the program.

**Understand → Analyze → Generate Tests → Execute → Compare → Learn**

## 🔮 Future Scope

- Support additional programming languages for execution.
- Improve code execution isolation and security.
- Add performance and memory analysis.
- Introduce AI-assisted debugging and code correction.
- Provide interactive coding exercises and quizzes.

## 👨‍💻 Author

**Muhammad Sumair Ali**  
Pallavi Engineering College  
CSE – Artificial Intelligence and Machine Learning  
2023–2027

## 📌 Project Links

- **Live Demo:** https://ai-code-explainer-ejnjpajhlkstt7ywq6tqtf.streamlit.app/
- **GitHub Repository:** https://github.com/Summerlah/ai-code-explainer
