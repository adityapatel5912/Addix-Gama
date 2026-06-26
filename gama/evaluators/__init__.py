"""
Module documentation.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path

from gama.schema import EvaluatorResult

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class BaseEvaluator(ABC):
    """
    Abstract base class for all Addix Gama evaluators.
    Enforces a strict, uniform interface for execution.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """The distinct name of the evaluator."""
        pass

    @abstractmethod
    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        """
        Executes the evaluation logic on the target directory.

        Args:
            target_dir (Path): The root directory of the codebase to evaluate.

        Returns:
            EvaluatorResult: A strictly typed Pydantic result containing pass/fail status and errors.
        """
        pass
