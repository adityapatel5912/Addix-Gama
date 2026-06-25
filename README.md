# Addix Gama

Addix Gama is an open-source, autonomous continuous-testing and validation engine designed to stress-test software repositories. It ensures codebases are entirely production-ready across database connections, authentication chains, security, and UI/UX layouts before deployment.

## 🚀 How It Works
Gama does not provide the primary LLM logic; it connects to external models via user-provided API keys. Its unique value is execution, verification, and orchestration:

1. **Scan:** Analyzes the target codebase across 5 core production vectors (Database, OAuth, Codebase Health, Security, and UI/UX).
2. **Assess:** Generates a highly detailed, instruction-optimized Markdown state file listing structural bugs, architectural gaps, and specific upgrade instructions.
3. **Repair Loop:** Feeds this Markdown context file directly to external engineering agents (like Claude Code or Antigravity), prompting them to apply the fixes.
4. **Verify:** Automatically re-runs all test assertions after file changes are detected. 
5. **Certify:** Repeats this loop recursively until all high-criticality bugs are fixed, then compiles a final, boardroom-ready Audit PDF Report.

## 📁 Repository Architecture

```text
addix-gama/
├── gama/
│   ├── __init__.py
│   ├── cli.py             # CLI entry point (Typer/Click commands)
│   ├── config.py          # Pydantic environment and API key management
│   ├── loop.py            # Recursive evaluation & external agent repair loop
│   ├── reporter.py        # Markdown parser & ReportLab PDF generation engine
│   └── evaluators/        # Specialized evaluation testing vectors
│       ├── __init__.py
│       ├── db_stress.py   # Database schema & connection health checks
│       ├── auth_check.py  # OAuth token and flow configuration verification
│       ├── security.py    # Static analysis & secret scanning
│       └── ui_ux.py       # Structural layout & frontend linting
└── tests/                 # Pytest suite for the Gama validation engine
⚙️ Development Requirements
​Python 3.10+
​Dependencies: fastapi, pydantic-settings, typer, reportlab, pytest, click
