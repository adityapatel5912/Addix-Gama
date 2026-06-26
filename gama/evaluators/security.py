"""
Module documentation.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from gama.evaluators import BaseEvaluator
from gama.schema import ErrorDetail, EvaluatorResult

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Common regex patterns for secrets
SECRET_PATTERNS = {
    "AWS Access Key": r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])",  # simplified
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{20,}",
    "Generic API Key": r"(?i)(?:api_key|secret|token)\s*=\s*['\"][a-zA-Z0-9_\-]+['\"]",
}

# Regex pattern for FastAPI/Flask style endpoints
# Matches lines with @app.get(... etc
ENDPOINT_PATTERN = r"@(?:app|router)\.(?:get|post|put|delete|patch)\(.*?\)"
# Regex pattern for checking dependencies
DEPENDS_PATTERN = r"Depends\(.*?\)"
SECURITY_PATTERN = r"Security\(.*?\)"


class SecurityEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "Security Evaluator"

    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        errors = []
        password_pattern = re.compile(r'password\s*=\s*["\'][^"\']+["\']')

        for path in target_dir.rglob("*.py"):
            if "tests" in str(path):
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    content = "".join(lines)

                    if password_pattern.search(content):
                        errors.append(
                            ErrorDetail(
                                file=str(path),
                                line=0,
                                issue="Hardcoded Password",
                                title="Hardcoded Password",
                                description="A hardcoded password was detected in the file.",
                                instructions="Remove the hardcoded password and use an environment variable or secret manager.",
                            )
                        )

                    for name, pattern in SECRET_PATTERNS.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            line_no = content.count("\n", 0, match.start()) + 1
                            errors.append(
                                ErrorDetail(
                                    file=str(path),
                                    line=line_no,
                                    issue=f"Hardcoded Secret Found",
                                    title="Hardcoded Secret",
                                    description=f"Matched pattern for {name}.",
                                    instructions="Remove the hardcoded secret and use an environment variable or secret manager.",
                                )
                            )

                    for i, line in enumerate(lines):
                        if re.search(ENDPOINT_PATTERN, line):
                            func_def = ""
                            for j in range(i + 1, min(i + 10, len(lines))):
                                func_def += lines[j]
                                if ":" in lines[j]:  # end of def
                                    break

                            if not re.search(
                                DEPENDS_PATTERN, func_def
                            ) and not re.search(SECURITY_PATTERN, func_def):
                                errors.append(
                                    ErrorDetail(
                                        file=str(path),
                                        line=i + 1,
                                        issue="Open Endpoint",
                                        title="Open Endpoint",
                                        description="Endpoint appears to lack authentication/authorization dependencies (Depends/Security).",
                                        instructions="Add authentication dependencies to the endpoint.",
                                    )
                                )
            except (OSError, PermissionError, UnicodeDecodeError) as e:
                logger.error(f"Error reading {path}: {e}")
            except Exception as e:
                logger.error(f"Unhandled error processing {path}: {e}")

        return EvaluatorResult(passed=len(errors) == 0, errors=errors)
