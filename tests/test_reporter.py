import os

import pytest

from gama.reporter import generate_audit_report
from gama.schema import (
    ErrorDetail,
    EvaluatorErrorAggregation,
    EvaluatorResult,
    StateContext,
    StateSummary,
)


def test_generate_audit_report(tmp_path):
    # Dummy StateContext Pydantic object
    state_context = StateContext(
        summary=StateSummary(total=4, passed=3, failed=1, success_rate=0.75),
        evaluator_results={"Test Evaluator": EvaluatorResult(passed=False, errors=[])},
        aggregated_errors=[
            EvaluatorErrorAggregation(
                evaluator="Test Evaluator",
                errors=[
                    ErrorDetail(
                        issue="Test Issue",
                        title="Test Failure",
                        description="This is a test error description.",
                        instructions="Fix the test error.",
                        severity="High",
                    )
                ],
            )
        ],
        overall_status="FAILED",
        timestamp=1234567890.0,
    )

    output_pdf = tmp_path / "test_report.pdf"

    # Generate the PDF
    generate_audit_report(state_context, str(output_pdf))

    # Assert PDF was created and has content
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0
