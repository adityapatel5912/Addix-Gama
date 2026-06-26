import time
from typing import List, Dict, Any, Protocol, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import xml.sax.saxutils

class EvaluatorProtocol(Protocol):
    """Protocol defining the expected interface for an evaluator."""
    @property
    def name(self) -> str:
        ...

    def evaluate(self, target_dir: str = ".") -> Dict[str, Any]:
        ...

def get_default_evaluators() -> List[EvaluatorProtocol]:
    from gama.evaluators import security, db_stress, auth_check, ui_ux
    return [
        security.SecurityEvaluator(),
        db_stress.DBStressEvaluator(),
        auth_check.AuthEvaluator(),
        ui_ux.UIUXEvaluator()
    ]

class StateManager:
    """
    Core state manager that runs evaluators sequentially, tracks pass/fail counts,
    gathers granular error details, and aggregates them into a unified,
    code-health state context dictionary.
    """
    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0
        self.error_details = []
        self.evaluator_results = {}

    def run(self, evaluators: Optional[List[EvaluatorProtocol]] = None, target_dir: str = ".") -> Dict[str, Any]:
        """
        Runs all provided evaluators sequentially. If none provided, instantiates the 4 default evaluators.
        """
        if evaluators is None:
            evaluators = get_default_evaluators()

        self.pass_count = 0
        self.fail_count = 0
        self.error_details = []
        self.evaluator_results = {}

        for evaluator in evaluators:
            try:
                result = evaluator.evaluate(target_dir=target_dir)
            except Exception as e:
                result = {
                    "passed": False,
                    "errors": [{"description": f"Unhandled exception in evaluator: {str(e)}", "title": "Evaluator Crash", "category": "Internal"}],
                }

            passed = result.get("passed", False)
            errors = result.get("errors", [])

            self.evaluator_results[evaluator.name] = result

            if passed:
                self.pass_count += 1
            else:
                self.fail_count += 1
                if errors:
                    self.error_details.append({
                        "evaluator": evaluator.name,
                        "errors": errors
                    })

        total = self.pass_count + self.fail_count
        success_rate = (self.pass_count / total) if total > 0 else 1.0

        state_context = {
            "summary": {
                "total": total,
                "passed": self.pass_count,
                "failed": self.fail_count,
                "success_rate": round(success_rate, 4),
            },
            "evaluator_results": self.evaluator_results,
            "aggregated_errors": self.error_details,
            "overall_status": "PASSED" if self.fail_count == 0 and total > 0 else "FAILED" if total > 0 else "NO_EVALUATORS",
            "timestamp": time.time()
        }

        return state_context

def generate_state_markdown(state_context: Dict[str, Any]) -> str:
    """
    Generates a beautifully written Markdown state instruction file from the state context.
    """
    if state_context.get("overall_status") == "PASSED":
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
    for err_info in state_context.get("aggregated_errors", []):
        evaluator_name = err_info.get("evaluator", "Unknown Evaluator")
        for failure in err_info.get("errors", []):
            if isinstance(failure, str):
                failure = {"description": failure, "title": "Failure", "category": evaluator_name}

            md += f"## Issue {issue_count}: {failure.get('title', 'Unknown Failure')}\n\n"
            md += f"**Category:** {failure.get('category', evaluator_name)}\n"
            md += f"**Severity:** {failure.get('severity', 'High')}\n\n"

            md += "### Description\n"
            desc = failure.get('description', 'No description provided.')
            md += f"{desc}\n\n"

            md += "### Required Action (Instructions for Agent)\n"
            md += f"> {failure.get('instructions', 'Please investigate and fix the issue.')}\n\n"

            if 'file' in failure:
                md += f"**Target File:** `{failure['file']}`\n"
                if 'line' in failure:
                    md += f"**Target Line:** {failure['line']}\n"
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
    """
    print(f"Watching for changes in: {target_dir}")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, target_dir, recursive=True)
    observer.start()

    try:
        while not event_handler.change_detected:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        raise
    finally:
        observer.stop()
        observer.join()

    print("Change detected. Resuming loop...")

def run_loop(target_dir: str, evaluators: Optional[List[EvaluatorProtocol]] = None):
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

        if state_context.get("overall_status") == "PASSED":
            print("No failures detected. Exiting loop.")
            break

        print("Failures detected. Pausing and waiting for file changes to re-evaluate...")
        watch_and_wait(target_dir)
