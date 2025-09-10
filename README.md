# allmcp

This repository contains an autonomous agent project (workagent) that demonstrates MCP-driven capability learning and execution.

Contents:
- `workagent/` — main agent application, Flask web API, MCP manager, capability learner, plugins, and tests.
- `config/`, `logs/`, `reports/` — configuration, logs, and generated reports.

Quick start (development):

1. Create and activate a Python virtual environment (Windows Powershell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r workagent/requirements.txt
```

3. Run the web app (development):

```powershell
python workagent/start.py
```

Notes:
- For production, run the app with a WSGI server (gunicorn on Linux or waitress on Windows).
- Review `workagent/requirements.txt` for the project's Python dependencies.
