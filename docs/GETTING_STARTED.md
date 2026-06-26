# Getting Started with Addix Gama

Welcome to Addix Gama! This guide will walk you through the installation process, setting up your environment, and running your first codebase audit.

## Installation

To get started, clone the repository and install the dependencies. The project requires Python 3.10 or higher.

```bash
git clone <repository_url>
cd addix-gama
pip install -r requirements.txt
```

Alternatively, you can install the dependencies directly:
```bash
pip install fastapi typer pydantic pydantic-settings reportlab pytest
```

## Environment Setup

Gama orchestrates external AI models to evaluate your codebase. You'll need to provide API keys for the models you intend to use.

Create a `.env` file in the root of the project and add your API keys. Gama's configuration (in `gama/config.py`) automatically loads these using `pydantic-settings`.

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Running an Initial Codebase Audit

Gama provides a Typer-based CLI for interacting with its validation engine.

### 1. The Scan Command
To run a one-off audit across all core production vectors (Database, OAuth, Security, UI/UX) and generate a state markdown file, run:

```bash
python -m gama.cli scan
```
This evaluates the target project and outputs a `gama_state.md` file. This file contains strict, context-rich instructions for external engineering agents to apply fixes.

### 2. The Loop Command
To start the automated repair loop, which continuously evaluates the project and watches for file changes (re-running once locks clear), use:

```bash
python -m gama.cli loop
```

### 3. Generate an Audit Report
Once your codebase is fully compliant and passes all evaluations, generate a final PDF audit report:

```bash
python -m gama.cli report
```
This will compile `gama_audit_report.pdf` from the internal Pydantic state model.
