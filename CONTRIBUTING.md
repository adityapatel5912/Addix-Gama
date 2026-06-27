# Contributing to Addix Gama

We welcome contributions to Addix Gama! This guide will help you get started.

## Getting Started

1. **Clone the repository:**
   ```
   git clone https://github.com/your-org/addix-gama.git
   cd addix-gama
   ```

2. **Set up the development environment:**
   We recommend using a virtual environment.
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   Install the exact locked dependencies from `requirements.txt`.
   ```
   pip install -r requirements.txt
   ```
   Or install the package in editable mode:
   ```
   pip install -e .
   ```

## Running Tests

We use `pytest` for our test suite. To run the tests, execute the following command from the root directory:

```
PYTHONPATH=. pytest tests/
```

Ensure all tests pass before submitting a Pull Request.

## Creating New Evaluators

Evaluators are the core of Gama's scanning engine. To create a new evaluator:

1. Create a new file in `gama/evaluators/` (e.g., `my_new_evaluator.py`).
2. Inherit from `BaseEvaluator` defined in `gama/evaluators/base.py`.
3. Implement the `name` property and the `evaluate(self, target_dir: Path) -> EvaluatorResult` method.
4. Ensure your `evaluate` method returns a valid `EvaluatorResult` (Pydantic model from `gama.schema`).
5. Register your new evaluator in `gama.loop.get_default_evaluators()`.
6. Add comprehensive tests for your evaluator in the `tests/` directory.

## Submitting a Pull Request

1. Create a new branch from `main` (e.g., `feature/my-new-feature` or `bugfix/issue-123`).
2. Make your changes, following the code style of the project.
3. Write clear and concise commit messages.
4. Run the test suite and ensure all tests pass.
5. Push your branch to your fork or the main repository.
6. Open a Pull Request against the `main` branch. Provide a detailed description of your changes and why they are necessary.

Thank you for contributing!
