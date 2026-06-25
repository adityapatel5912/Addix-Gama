import os
import re
from typing import List, Dict, Any

# Common regex patterns for secrets
SECRET_PATTERNS = {
    "AWS Access Key": r"(?<![A-Z0-9])[A-Z0-9]{20}(?![A-Z0-9])", # simplified
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{20,}",
    "Generic API Key": r"(?i)(?:api_key|secret|token)\s*=\s*['\"][a-zA-Z0-9_\-]+['\"]"
}

# Regex pattern for FastAPI/Flask style endpoints
# Matches lines with @app.get(... etc
ENDPOINT_PATTERN = r"@(?:app|router)\.(?:get|post|put|delete|patch)\(.*?\)"
# Regex pattern for checking dependencies
DEPENDS_PATTERN = r"Depends\(.*?\)"
SECURITY_PATTERN = r"Security\(.*?\)"

def scan_hardcoded_secrets(project_path: str) -> List[Dict[str, Any]]:
    findings = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                    for name, pattern in SECRET_PATTERNS.items():
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            # Avoid matching common words or random non-secrets if needed
                            # Calculate line number
                            line_no = content.count('\n', 0, match.start()) + 1
                            findings.append({
                                "file": filepath,
                                "line": line_no,
                                "issue": f"Hardcoded Secret Found",
                                "detail": f"Matched pattern for {name}"
                            })
            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return findings

def scan_open_endpoints(project_path: str) -> List[Dict[str, Any]]:
    findings = []

    for root, _, files in os.walk(project_path):
        for file in files:
            if not file.endswith('.py'):
                continue

            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                    for i, line in enumerate(lines):
                        if re.search(ENDPOINT_PATTERN, line):
                            # Found an endpoint decorator.
                            # Look at the next few lines for the function definition to see if it has auth
                            # This is a naive static analysis, checking the function signature
                            # usually the function def is right below the decorator
                            func_def = ""
                            for j in range(i + 1, min(i + 10, len(lines))):
                                func_def += lines[j]
                                if ":" in lines[j]: # end of def
                                    break

                            if not re.search(DEPENDS_PATTERN, func_def) and not re.search(SECURITY_PATTERN, func_def):
                                findings.append({
                                    "file": filepath,
                                    "line": i + 1,
                                    "issue": "Open Endpoint",
                                    "detail": "Endpoint appears to lack authentication/authorization dependencies (Depends/Security)."
                                })

            except Exception as e:
                print(f"Error reading {filepath}: {e}")

    return findings
