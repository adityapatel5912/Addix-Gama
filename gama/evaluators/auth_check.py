import re
from pathlib import Path
from typing import List, Dict, Any

class AuthEvaluator:
    @property
    def name(self) -> str:
        return "Authentication Evaluator"

    def evaluate(self, target_dir: str = ".") -> Dict[str, Any]:
        issues = []
        extensions_to_check = {'.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.env', '.html'}

        for path in Path(target_dir).rglob('*'):
            if "tests" in str(path):
                continue
            if path.is_file() and path.suffix in extensions_to_check:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 1. Check for insecure redirect_uri (http:// except localhost) in code assignments
                    redirect_uri_pattern = re.compile(r"""redirect_uri\s*[:=]\s*['"](http://(?!(localhost|127\.0\.0\.1))[^'"]+)['"]""", re.IGNORECASE)
                    for match in redirect_uri_pattern.finditer(content):
                        issues.append({
                            "type": "insecure_oauth_redirect",
                            "file": str(path),
                            "issue": "Insecure HTTP redirect_uri",
                            "title": "Insecure HTTP redirect_uri",
                            "description": f"Insecure HTTP redirect_uri assignment found: {match.group(1)}",
                            "instructions": "Use HTTPS for redirect URIs, unless using localhost.",
                            "line": content[:match.start()].count('\n') + 1
                        })

                    # 2. Check for insecure redirect_uri in URLs/query strings
                    query_redirect_pattern = re.compile(r"""redirect_uri=http://(?!(localhost|127\.0\.0\.1))[^&\s'"]+""", re.IGNORECASE)
                    for match in query_redirect_pattern.finditer(content):
                        issues.append({
                            "type": "insecure_oauth_redirect",
                            "file": str(path),
                            "issue": "Insecure HTTP redirect_uri",
                            "title": "Insecure HTTP redirect_uri",
                            "description": f"Insecure HTTP redirect_uri found in query string: {match.group(0)}",
                            "instructions": "Use HTTPS for redirect URIs, unless using localhost.",
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
                                    "file": str(path),
                                    "issue": "Missing OAuth state",
                                    "title": "Missing OAuth state parameter",
                                    "description": f"OAuth authorization URL missing 'state' parameter: {url}",
                                    "instructions": "Include a 'state' parameter in OAuth authorization requests to prevent CSRF attacks.",
                                    "line": content[:match.start()].count('\n') + 1
                                })

                except Exception:
                    pass

        return {
            "passed": len(issues) == 0,
            "errors": issues
        }
