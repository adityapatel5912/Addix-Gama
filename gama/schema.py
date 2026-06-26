from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ErrorDetail(BaseModel):
    file: Optional[str] = Field(None, description="Path to the file where the error was found.")
    line: Optional[int] = Field(None, description="Line number where the error was found.")
    issue: str = Field(..., description="Short type/category of the issue.")
    title: str = Field(..., description="Title of the issue.")
    description: str = Field(..., description="Detailed description of the issue.")
    instructions: str = Field(..., description="Instructions on how to fix the issue.")
    severity: str = Field("High", description="Severity level of the issue.")

class EvaluatorResult(BaseModel):
    passed: bool = Field(..., description="Whether the evaluation passed or failed.")
    errors: List[ErrorDetail] = Field(default_factory=list, description="List of errors found during evaluation.")

class EvaluatorErrorAggregation(BaseModel):
    evaluator: str = Field(..., description="Name of the evaluator.")
    errors: List[ErrorDetail] = Field(..., description="Errors found by this evaluator.")

class StateSummary(BaseModel):
    total: int = Field(..., description="Total number of evaluators run.")
    passed: int = Field(..., description="Number of evaluators that passed.")
    failed: int = Field(..., description="Number of evaluators that failed.")
    success_rate: float = Field(..., description="Ratio of passed to total evaluators.")

class StateContext(BaseModel):
    summary: StateSummary = Field(..., description="Summary of the evaluation run.")
    evaluator_results: Dict[str, EvaluatorResult] = Field(..., description="Results per evaluator.")
    aggregated_errors: List[EvaluatorErrorAggregation] = Field(default_factory=list, description="All errors aggregated by evaluator.")
    overall_status: str = Field(..., description="Overall status (e.g., 'PASSED', 'FAILED', 'NO_EVALUATORS').")
    timestamp: float = Field(..., description="Unix timestamp of the evaluation.")
