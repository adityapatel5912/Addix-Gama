import pytest
import os
from pathlib import Path
from gama.loop import StateManager
from gama.evaluators import BaseEvaluator
from gama.schema import EvaluatorResult, ErrorDetail, StateContext

class MockPassEvaluator(BaseEvaluator):
    @property
    def name(self):
        return "PassEvaluator"

    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        return EvaluatorResult(passed=True, errors=[])

class MockFailEvaluator(BaseEvaluator):
    @property
    def name(self):
        return "FailEvaluator"

    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        return EvaluatorResult(
            passed=False,
            errors=[
                ErrorDetail(
                    issue="General Failure",
                    title="Failure",
                    description="A terrible error occurred",
                    instructions="Fix the failure"
                )
            ]
        )

class MockExceptionEvaluator(BaseEvaluator):
    @property
    def name(self):
        return "ExceptionEvaluator"

    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        raise RuntimeError("Something went horribly wrong")

def test_state_manager_all_pass():
    manager = StateManager()
    evaluators = [MockPassEvaluator(), MockPassEvaluator()]

    state_context = manager.run(evaluators)

    assert isinstance(state_context, StateContext)
    assert state_context.summary.total == 2
    assert state_context.summary.passed == 2
    assert state_context.summary.failed == 0
    assert state_context.overall_status == "PASSED"
    assert len(state_context.aggregated_errors) == 0

def test_state_manager_mixed_results():
    manager = StateManager()
    evaluators = [MockPassEvaluator(), MockFailEvaluator()]

    state_context = manager.run(evaluators)

    assert state_context.summary.total == 2
    assert state_context.summary.passed == 1
    assert state_context.summary.failed == 1
    assert state_context.summary.success_rate == 0.5
    assert state_context.overall_status == "FAILED"

    assert len(state_context.aggregated_errors) == 1
    error_detail = state_context.aggregated_errors[0]
    assert error_detail.evaluator == "FailEvaluator"
    assert len(error_detail.errors) == 1
    assert "A terrible error occurred" in error_detail.errors[0].description

def test_state_manager_with_exception():
    manager = StateManager()
    evaluators = [MockExceptionEvaluator()]

    state_context = manager.run(evaluators)

    assert state_context.summary.total == 1
    assert state_context.summary.passed == 0
    assert state_context.summary.failed == 1
    assert state_context.overall_status == "FAILED"

    assert len(state_context.aggregated_errors) == 1
    error_detail = state_context.aggregated_errors[0]
    assert error_detail.evaluator == "ExceptionEvaluator"
    assert "Unhandled exception" in error_detail.errors[0].description

def test_state_manager_empty_evaluators():
    manager = StateManager()
    state_context = manager.run([])

    assert state_context.summary.total == 0
    assert state_context.summary.passed == 0
    assert state_context.overall_status == "NO_EVALUATORS"
