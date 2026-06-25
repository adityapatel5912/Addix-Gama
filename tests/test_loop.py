import pytest
from typing import Dict, Any
from gama.loop import StateManager, EvaluatorProtocol

class MockPassEvaluator:
    @property
    def name(self) -> str:
        return "PassEvaluator"

    def evaluate(self) -> Dict[str, Any]:
        return {
            "passed": True,
            "errors": []
        }

class MockFailEvaluator:
    @property
    def name(self) -> str:
        return "FailEvaluator"

    def evaluate(self) -> Dict[str, Any]:
        return {
            "passed": False,
            "errors": ["Connection refused", "Timeout occurred"]
        }

class MockExceptionEvaluator:
    @property
    def name(self) -> str:
        return "ExceptionEvaluator"

    def evaluate(self) -> Dict[str, Any]:
        raise RuntimeError("Something went horribly wrong")

def test_state_manager_all_pass():
    manager = StateManager()
    evaluators = [MockPassEvaluator(), MockPassEvaluator()]

    state_context = manager.run(evaluators)

    assert state_context["summary"]["total"] == 2
    assert state_context["summary"]["passed"] == 2
    assert state_context["summary"]["failed"] == 0
    assert state_context["summary"]["success_rate"] == 1.0
    assert state_context["overall_status"] == "PASSED"
    assert len(state_context["aggregated_errors"]) == 0
    assert "timestamp" in state_context

def test_state_manager_mixed_results():
    manager = StateManager()
    evaluators = [MockPassEvaluator(), MockFailEvaluator()]

    state_context = manager.run(evaluators)

    assert state_context["summary"]["total"] == 2
    assert state_context["summary"]["passed"] == 1
    assert state_context["summary"]["failed"] == 1
    assert state_context["summary"]["success_rate"] == 0.5
    assert state_context["overall_status"] == "FAILED"

    assert len(state_context["aggregated_errors"]) == 1
    error_detail = state_context["aggregated_errors"][0]
    assert error_detail["evaluator"] == "FailEvaluator"
    assert error_detail["errors"] == ["Connection refused", "Timeout occurred"]

    assert "PassEvaluator" in state_context["evaluator_results"]
    assert "FailEvaluator" in state_context["evaluator_results"]

def test_state_manager_with_exception():
    manager = StateManager()
    evaluators = [MockExceptionEvaluator()]

    state_context = manager.run(evaluators)

    assert state_context["summary"]["total"] == 1
    assert state_context["summary"]["passed"] == 0
    assert state_context["summary"]["failed"] == 1
    assert state_context["overall_status"] == "FAILED"

    assert len(state_context["aggregated_errors"]) == 1
    error_detail = state_context["aggregated_errors"][0]
    assert error_detail["evaluator"] == "ExceptionEvaluator"
    assert "Unhandled exception" in error_detail["errors"][0]

def test_state_manager_empty_evaluators():
    manager = StateManager()

    state_context = manager.run([])

    assert state_context["summary"]["total"] == 0
    assert state_context["summary"]["passed"] == 0
    assert state_context["summary"]["failed"] == 0
    assert state_context["summary"]["success_rate"] == 1.0
    assert state_context["overall_status"] == "NO_EVALUATORS"
    assert len(state_context["aggregated_errors"]) == 0
