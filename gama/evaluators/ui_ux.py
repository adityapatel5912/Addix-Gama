import re
from pathlib import Path
from typing import List, Dict

def evaluate_ui_code(content: str, filepath: str = "") -> List[Dict[str, str]]:
    """
    Evaluates source code for common UI/UX structural issues.
    Focuses on:
    - Structural styling flaws (e.g., usage of inline styles style={})
    - Misconfigured production layout wrappers (e.g., missing top-level <Layout> or <Provider>)
    """
    issues = []

    # 1. Structural styling flaws: Catch inline styles (style={{...}} or style="...")
    # This is a basic regex, could be improved with AST parsing for more accurate results
    inline_style_pattern_react = re.compile(r"""style=\{\{.*?\}\}""", re.DOTALL)
    for match in inline_style_pattern_react.finditer(content):
        issues.append({
            "type": "inline_styles",
            "file": filepath,
            "message": "Inline style object detected (style={{...}}). Prefer CSS modules or styled-components.",
            "line": content[:match.start()].count('\n') + 1
        })

    inline_style_pattern_html = re.compile(r"""style=['"].*?['"]""", re.IGNORECASE)
    for match in inline_style_pattern_html.finditer(content):
        # Filter out common false positives or valid uses like style="display: none" if needed
        issues.append({
            "type": "inline_styles",
            "file": filepath,
            "message": f"Inline style attribute detected: {match.group(0)}. Prefer external CSS.",
            "line": content[:match.start()].count('\n') + 1
        })

    # 2. Misconfigured production layout wrappers
    # Check if a file looks like a main page/app entry but is missing a <Layout> or Provider wrapper
    # Simple heuristic: if it contains "export default" and JSX-like return, does it have Layout?
    if 'export default ' in content and ('return (' in content or 'return <' in content):
        if not re.search(r"""<(Layout|Provider|AppProvider|ThemeProvider)\b""", content):
            # It's a heuristic, so we might want to only flag files in specific directories like pages/ or app/
            # For this evaluator, we'll raise an info/warning issue if it looks like a main component
            # A more advanced check would parse the AST and ensure the top-level return is wrapped.

            # Additional heuristic: check if it returns a plain <div> or <main> at the root
            root_return_pattern = re.compile(r"""return\s*\(\s*<(div|main|section|article)\b""")
            if root_return_pattern.search(content):
                issues.append({
                    "type": "missing_layout_wrapper",
                    "file": filepath,
                    "message": "Main component appears to return raw HTML elements without a top-level <Layout> or <Provider> wrapper.",
                    "line": 0 # General file issue
                })

    return issues

def scan_directory(directory: str) -> List[Dict[str, str]]:
    """Recursively scans a directory for UI/UX issues."""
    all_issues = []
    extensions_to_check = {'.js', '.jsx', '.ts', '.tsx', '.html'}

    for path in Path(directory).rglob('*'):
        if path.is_file() and path.suffix in extensions_to_check:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                issues = evaluate_ui_code(content, str(path))
                all_issues.extend(issues)
            except Exception:
                pass
    return all_issues
