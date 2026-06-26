import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from gama.evaluators import BaseEvaluator
from gama.schema import (
    ErrorDetail,
    EvaluatorErrorAggregation,
    EvaluatorResult,
    StateContext,
    StateSummary,
)


def get_default_evaluators() -> List[BaseEvaluator]:
    from gama.evaluators import auth_check, db_stress, security, ui_ux

    return [
        security.SecurityEvaluator(),
        db_stress.DBStressEvaluator(),
        auth_check.AuthEvaluator(),
        ui_ux.UIUXEvaluator(),
    ]


class StateManager:
    """
    Core state manager that runs evaluators sequentially, tracks pass/fail counts,
    gathers granular error details, and aggregates them into a unified,
    code-health state context strictly typed with Pydantic.
    """

    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0
        self.error_details: List[EvaluatorErrorAggregation] = []
        self.evaluator_results: Dict[str, EvaluatorResult] = {}

    def run(
        self, evaluators: Optional[List[BaseEvaluator]] = None, target_dir: str = "."
    ) -> StateContext:
        """
        Runs all provided evaluators sequentially. If none provided, instantiates the default evaluators.
        """
        if evaluators is None:
            evaluators = get_default_evaluators()

        self.pass_count = 0
        self.fail_count = 0
        self.error_details = []
        self.evaluator_results = {}
        target_path = Path(target_dir)

        for evaluator in evaluators:
            try:
                result = evaluator.evaluate(target_dir=target_path)
            except Exception as e:
                result = EvaluatorResult(
                    passed=False,
                    errors=[
                        ErrorDetail(
                            issue="Evaluator Crash",
                            title="Evaluator Crash",
                            description=f"Unhandled exception in evaluator: {str(e)}",
                            instructions="Check evaluator implementation.",
                            severity="Critical",
                        )
                    ],
                )

            self.evaluator_results[evaluator.name] = result

            if result.passed:
                self.pass_count += 1
            else:
                self.fail_count += 1
                if result.errors:
                    self.error_details.append(
                        EvaluatorErrorAggregation(
                            evaluator=evaluator.name, errors=result.errors
                        )
                    )

        total = self.pass_count + self.fail_count
        success_rate = (self.pass_count / total) if total > 0 else 1.0

        summary = StateSummary(
            total=total,
            passed=self.pass_count,
            failed=self.fail_count,
            success_rate=round(success_rate, 4),
        )

        overall_status = (
            "PASSED"
            if self.fail_count == 0 and total > 0
            else "FAILED" if total > 0 else "NO_EVALUATORS"
        )

        return StateContext(
            summary=summary,
            evaluator_results=self.evaluator_results,
            aggregated_errors=self.error_details,
            overall_status=overall_status,
            timestamp=time.time(),
        )


def generate_state_markdown(state_context: StateContext) -> str:
    """
    Generates a beautifully written Markdown state instruction file from the StateContext model.
    """
    if state_context.overall_status == "PASSED":
        return (
            "# Gama State Report\n\n"
            "## All Systems Go\n\n"
            "No failures detected in the target project. The codebase is currently fully operational and production-ready.\n"
        )

    md = "# Gama State Report: System Failures Detected\n\n"
    md += "The following high-criticality bugs and structural gaps were identified during the automated testing phase. "
    md += "External coding agents, please follow the explicit instructions provided below to repair the codebase.\n\n"
    md += "---\n\n"

    issue_count = 1
    for err_info in state_context.aggregated_errors:
        evaluator_name = err_info.evaluator
        for failure in err_info.errors:
            md += f"## Issue {issue_count}: {failure.title}\n\n"
            md += f"**Category:** {evaluator_name}\n"
            md += f"**Severity:** {failure.severity}\n\n"

            md += "### Description\n"
            md += f"{failure.description}\n\n"

            md += "### Required Action (Instructions for Agent)\n"
            md += f"> {failure.instructions}\n\n"

            if failure.file:
                md += f"**Target File:** `{failure.file}`\n"
                if failure.line:
                    md += f"**Target Line:** {failure.line}\n"
            md += "\n---\n\n"
            issue_count += 1

    md += "\n## Next Steps\n"
    md += "Once the repairs have been applied, save the files. The Gama loop will automatically detect the changes and re-evaluate the repository.\n"
    return md


def write_state_file(markdown_content: str, file_path: str = "gama_state.md"):
    """
    Writes the generated markdown content to the specified file path.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"State file written to {file_path}")


class ChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.change_detected = False

    def on_modified(self, event):
        if not event.is_directory and "gama_state.md" not in event.src_path:
            self.change_detected = True

    def on_created(self, event):
        if not event.is_directory and "gama_state.md" not in event.src_path:
            self.change_detected = True


def watch_and_wait(target_dir: str):
    """
    Uses watchdog to monitor the target_dir and blocks execution until a file change is detected.
    Adds a short grace period after detecting a file change to ensure IO locks are cleared before re-evaluating.
    """
    print(f"Watching for changes in: {target_dir}")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, target_dir, recursive=True)
    observer.start()

    try:
        while not event_handler.change_detected:
            time.sleep(1)

        # Grace period for async IO safety
        print("Change detected. Waiting 1s for file locks to clear...")
        time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        raise
    finally:
        observer.stop()
        observer.join()

    print("Resuming loop...")


def run_loop(target_dir: str, evaluators: Optional[List[BaseEvaluator]] = None):
    """
    Implements the continuous testing loop.
    Repeatedly evaluates the project, writes the state file, and waits for changes if there are failures.
    """
    if evaluators is None:
        evaluators = get_default_evaluators()

    state_manager = StateManager()

    while True:
        print("Evaluating project...")
        state_context = state_manager.run(evaluators, target_dir=target_dir)

        markdown_content = generate_state_markdown(state_context)
        write_state_file(markdown_content)

        if state_context.overall_status == "PASSED":
            print("No failures detected. Exiting loop.")
            break

        print(
            "Failures detected. Pausing and waiting for file changes to re-evaluate..."
        )
        watch_and_wait(target_dir)
