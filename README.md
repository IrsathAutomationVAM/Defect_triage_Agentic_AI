# Defect Triage Agentic AI

A lightweight Python-based defect triage agent for Windows that classifies incoming bug reports into:

- Severity
- Priority
- Module impact
- Suggested owner
- Missing information
- Confidence score
- Human review requirement

The project uses Python and can work with Ollama via the `qwen2:7b` model when available. If Ollama is not reachable, the agent falls back to a deterministic heuristic-based triage so it can still run locally on Windows.

## Project Structure

- `agent.py` - entry point for running the agent
- `workflow.py` - triage workflow, Ollama integration, and fallback logic
- `prompts.py` - prompt construction for the LLM
- `schemas.py` - input/output data models
- `sample_defects.json` - sample defect payloads for testing
- `tests/test_agent.py` - regression test for the triage output contract
- `run_agent.cmd` - Windows Command Prompt launcher
- `run_agent.ps1` - Windows PowerShell launcher

## Prerequisites

- Windows 10 or 11
- Python 3.9+ installed and added to PATH
- Optional: Ollama installed and running locally

### Install Ollama on Windows

If you want to use the LLM path instead of the fallback logic:

1. Install Ollama from https://ollama.com/
2. Start the service from Command Prompt or PowerShell:

```powershell
ollama serve
```

3. Pull the model:

```powershell
ollama pull qwen2:7b
```

## Setup on Windows

Open PowerShell in the folder where you want to clone the repository:

```powershell
git clone <repository-url>
cd Defect_triage_Agentic_AI
```

Create and activate a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution, run this once in the current session:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## Run the Agent on Windows

### Option 1: PowerShell

```powershell
py agent.py
```

### Option 2: Double-click launcher

Run the file `run_agent.cmd` from File Explorer.

### Option 3: PowerShell launcher

```powershell
powershell -ExecutionPolicy Bypass -File .\run_agent.ps1
```

Example output:

```python
{
  "severity": "high",
  "priority": "p1",
  "module_impact": "checkout",
  "suggested_owner": "payments team",
  "missing_information": [],
  "confidence_score": 0.78,
  "needs_human_review": true
}
```

## Test the Agent on Windows

Run the test suite:

```powershell
pytest -q
```

## Customize Input

You can test the agent with your own defect payload by editing the sample in `agent.py` or by passing a dictionary into the triage function from Python:

```python
from agent import run_triage

payload = {
    "bug_description": "Checkout page throws error after payment confirmation",
    "logs": "500 Internal Server Error",
    "screenshot_notes": "Button remains disabled",
    "additional_comments": "Reported by a customer"
}

print(run_triage(payload))
```

## Notes

- The implementation is structured for Windows execution and supports both local fallback execution and optional Ollama-based reasoning.
- If Ollama is unavailable, the system still returns a valid triage result using heuristics.
- The agent is designed to be extended with richer prompt engineering, better classification logic, or integration into a larger workflow engine.
