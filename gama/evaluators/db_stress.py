import os
import re
from typing import List, Dict, Any

# SQLAlchemy / generic connection creation patterns
# e.g., create_engine(...) or Session(...)
ENGINE_PATTERN = r"create_engine\((.*?)\)"
CONNECT_PATTERN = r"(?:psycopg2|pymysql|mysql\.connector|sqlite3)\.connect\((.*?)\)"

# We look for arguments indicating pool limits or timeouts inside the instantiation
POOL_SIZE_PATTERN = r"pool_size\s*="
MAX_OVERFLOW_PATTERN = r"max_overflow\s*="
TIMEOUT_PATTERN = r"(?:connect_timeout|timeout)\s*="

def scan_insecure_pooling(project_path: str) -> List[Dict[str, Any]]:
    findings = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Search for engine creations
                    for match in re.finditer(ENGINE_PATTERN, content, re.DOTALL):
                        engine_args = match.group(1)
                        # We just naive check if the args contain pooling config
                        # if they are using default pool, it could be insecure under stress
                        if not re.search(POOL_SIZE_PATTERN, engine_args) or not re.search(MAX_OVERFLOW_PATTERN, engine_args):
                            line_no = content.count('\n', 0, match.start()) + 1
                            findings.append({
                                "file": filepath,
                                "line": line_no,
                                "issue": "Insecure Database Pooling",
                                "detail": "Database connection found without explicit 'pool_size' or 'max_overflow' configuration."
                            })

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return findings

def scan_unhandled_timeouts(project_path: str) -> List[Dict[str, Any]]:
    findings = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Search for engine creations and direct connections
                    # Combine patterns
                    for pattern in [ENGINE_PATTERN, CONNECT_PATTERN]:
                        for match in re.finditer(pattern, content, re.DOTALL):
                            conn_args = match.group(1)

                            if not re.search(TIMEOUT_PATTERN, conn_args):
                                line_no = content.count('\n', 0, match.start()) + 1
                                findings.append({
                                    "file": filepath,
                                    "line": line_no,
                                    "issue": "Unhandled Database Timeout",
                                    "detail": "Database connection found without explicit 'connect_timeout' or 'timeout' configuration."
                                })

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return findings
