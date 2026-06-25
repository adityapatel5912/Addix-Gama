import time
from typing import List, Dict, Any, Protocol

class EvaluatorProtocol(Protocol):
    """Protocol defining the expected interface for an evaluator."""
    @property
    def name(self) -> str:
        ...

    def evaluate(self) -> Dict[str, Any]:
        """
        Executes the evaluation.
        Returns a dictionary containing at least:
        - 'passed': bool
        - 'errors': list of strings or granular error details (if any)
        """
        ...

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

    def run(self, evaluators: List[EvaluatorProtocol]) -> Dict[str, Any]:
        """
        Runs all provided evaluators sequentially.

        Args:
            evaluators: A list of objects matching the EvaluatorProtocol.

        Returns:
            A unified, code-health state context dictionary.
        """
        self.pass_count = 0
        self.fail_count = 0
        self.error_details = []
        self.evaluator_results = {}

        for evaluator in evaluators:
            try:
                result = evaluator.evaluate()
            except Exception as e:
                result = {
                    "passed": False,
                    "errors": [f"Unhandled exception in evaluator: {str(e)}"],
                }

            passed = result.get("passed", False)
            errors = result.get("errors", [])

            # Store the raw result
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
