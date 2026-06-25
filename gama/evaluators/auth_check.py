import re
from pathlib import Path
from typing import List, Dict

def evaluate_auth_code(content: str, filepath: str = "") -> List[Dict[str, str]]:
    """
    Evaluates source code for common authentication vulnerabilities.
    Focuses on OAuth misconfigurations:
    - Insecure redirect URIs (using HTTP instead of HTTPS, except localhost)
    - Missing state parameters in authorization requests
    """
    issues = []

    # 1. Check for insecure redirect_uri (http:// except localhost) in code assignments
    redirect_uri_pattern = re.compile(r"""redirect_uri\s*[:=]\s*['"](http://(?!(localhost|127\.0\.0\.1))[^'"]+)['"]""", re.IGNORECASE)
    for match in redirect_uri_pattern.finditer(content):
        issues.append({
            "type": "insecure_oauth_redirect",
            "file": filepath,
            "message": f"Insecure HTTP redirect_uri assignment found: {match.group(1)}",
            "line": content[:match.start()].count('\n') + 1
        })

    # 2. Check for insecure redirect_uri in URLs/query strings
    query_redirect_pattern = re.compile(r"""redirect_uri=http://(?!(localhost|127\.0\.0\.1))[^&\s'"]+""", re.IGNORECASE)
    for match in query_redirect_pattern.finditer(content):
        issues.append({
            "type": "insecure_oauth_redirect",
            "file": filepath,
            "message": f"Insecure HTTP redirect_uri found in query string: {match.group(0)}",
            "line": content[:match.start()].count('\n') + 1
        })

    # 3. Check for missing state tokens in OAuth authorization URLs
    # Looking for URLs containing 'client_id=' and 'response_type=' or 'authorize' but missing 'state='
    oauth_url_pattern = re.compile(r"""['"`](https?://[^'"`]+)['"`]""", re.IGNORECASE)
    for match in oauth_url_pattern.finditer(content):
        url = match.group(1)
        if 'client_id=' in url and ('response_type=' in url or '/authorize' in url):
            if 'state=' not in url:
                issues.append({
                    "type": "missing_oauth_state",
                    "file": filepath,
                    "message": f"OAuth authorization URL missing 'state' parameter: {url}",
                    "line": content[:match.start()].count('\n') + 1
                })

    return issues

def scan_directory(directory: str) -> List[Dict[str, str]]:
    """Recursively scans a directory for authentication issues."""
    all_issues = []
    extensions_to_check = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.env', '.html'}

    for path in Path(directory).rglob('*'):
        if path.is_file() and path.suffix in extensions_to_check:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                issues = evaluate_auth_code(content, str(path))
                all_issues.extend(issues)
            except Exception:
                pass
    return all_issues
