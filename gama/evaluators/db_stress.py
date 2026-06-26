"""
Module documentation.
"""

import logging
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


# SQLAlchemy / generic connection creation patterns
# e.g., create_engine(...) or Session(...)
ENGINE_PATTERN = r"create_engine\((.*?)\)"
CONNECT_PATTERN = r"(?:psycopg2|pymysql|mysql\.connector|sqlite3)\.connect\((.*?)\)"

# We look for arguments indicating pool limits or timeouts inside the instantiation
POOL_SIZE_PATTERN = r"pool_size\s*="
MAX_OVERFLOW_PATTERN = r"max_overflow\s*="
TIMEOUT_PATTERN = r"(?:connect_timeout|timeout)\s*="


class DBStressEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "Database Stress Evaluator"

    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        errors = []
        broken_db_pattern = re.compile(r'db\s*=\s*["\']broken_connection.*?["\']')

        for path in target_dir.rglob("*.py"):
            if "tests" in str(path):
                continue

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()

                    if broken_db_pattern.search(content):
                        errors.append(
                            ErrorDetail(
                                file=str(path),
                                line=0,
                                issue="Broken Database Connection",
                                title="Broken DB Connection",
                                description="A hardcoded broken database connection string was detected.",
                                instructions="Remove or update the broken connection string to a valid one.",
                            )
                        )

                    # Search for engine creations
                    for match in re.finditer(ENGINE_PATTERN, content, re.DOTALL):
                        engine_args = match.group(1)
                        # We just naive check if the args contain pooling config
                        # if they are using default pool, it could be insecure under stress
                        if not re.search(
                            POOL_SIZE_PATTERN, engine_args
                        ) or not re.search(MAX_OVERFLOW_PATTERN, engine_args):
                            line_no = content.count("\n", 0, match.start()) + 1
                            errors.append(
                                ErrorDetail(
                                    file=str(path),
                                    line=line_no,
                                    issue="Insecure Database Pooling",
                                    title="Insecure DB Pooling",
                                    description="Database connection found without explicit 'pool_size' or 'max_overflow' configuration.",
                                    instructions="Configure 'pool_size' and 'max_overflow' for database engines.",
                                )
                            )

                    for pattern in [ENGINE_PATTERN, CONNECT_PATTERN]:
                        for match in re.finditer(pattern, content, re.DOTALL):
                            conn_args = match.group(1)

                            if not re.search(TIMEOUT_PATTERN, conn_args):
                                line_no = content.count("\n", 0, match.start()) + 1
                                errors.append(
                                    ErrorDetail(
                                        file=str(path),
                                        line=line_no,
                                        issue="Unhandled Database Timeout",
                                        title="Unhandled DB Timeout",
                                        description="Database connection found without explicit 'connect_timeout' or 'timeout' configuration.",
                                        instructions="Configure 'connect_timeout' or 'timeout' for database connections.",
                                    )
                                )

            except (OSError, PermissionError, UnicodeDecodeError) as e:
                logger.error(f"Error reading {path}: {e}")
            except Exception as e:
                logger.error(f"Unhandled error processing {path}: {e}")

        return EvaluatorResult(passed=len(errors) == 0, errors=errors)
