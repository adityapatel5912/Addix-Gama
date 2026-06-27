# Core Concepts & Architecture

Gama is engineered to be an autonomous continuous-testing and validation bridge between raw codebases and external AI coding agents. Its primary role is execution, verification, and orchestration—not direct LLM logic.

## The 5 Evaluation Vectors

Gama scans the target repository against five critical production vectors to ensure the codebase is robust, secure, and production-ready:

1.  **Security:** Static analysis and secret scanning to detect vulnerabilities, exposed keys, and insecure configurations.
2.  **DB Stress (Database):** Validation of database schemas, connection health, connection pooling, and indexing strategies.
3.  **OAuth:** Verification of authentication chains, token handling, and OAuth flow configurations.
4.  **Codebase Health:** General structural integrity checks, dead-code analysis, and adherence to established coding patterns.
5.  **UI/UX:** Structural layout verification and frontend linting to ensure design consistency and responsiveness.

Each of these vectors is implemented as an evaluator class inheriting from the `BaseEvaluator` abstract class (e.g., `SecurityEvaluator`, `DBStressEvaluator`).

## The Unified Data Schema

To guarantee strict, immutable data integrity across the orchestration bridge, Gama relies heavily on Pydantic models. This completely eliminates loose dictionary parsing errors between the evaluators and the reporting engines.

The data flow works as follows:

1.  **Evaluator Execution:** When `StateManager.run()` executes, each evaluator runs its `evaluate(self, target_dir)` method.
2.  **Strict Results (`EvaluatorResult`):** Each evaluator returns an `EvaluatorResult` object. If it fails, it populates a list of `ErrorDetail` objects. These detail objects include precise locations (`file`, `line`), categories (`issue`, `title`), severity, and actionable `instructions`.
3.  **Aggregation (`StateContext`):** The `StateManager` aggregates all `EvaluatorResult` objects into a single, master `StateContext` Pydantic model. This model includes a `StateSummary` (pass/fail counts) and all `EvaluatorErrorAggregation` lists.
4.  **Deterministic Output:**
    *   **Markdown Generation:** The `generate_state_markdown()` function parses the strictly typed `StateContext` directly to generate the instruction-optimized `gama_state.md` file for external AI agents.
    *   **Report Generation:** The PDF reporter (using `reportlab`) takes the exact same `StateContext` instance to construct the final boardroom-ready `gama_audit_report.pdf`.

By enforcing this strict Pydantic architecture (`gama/schema.py`), Gama ensures that the context provided to LLM repair agents and the final audit reports remain completely synchronized and structurally sound.
