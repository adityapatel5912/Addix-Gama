import re
from pathlib import Path
from typing import List, Dict, Any

from gama.evaluators import BaseEvaluator
from gama.schema import EvaluatorResult, ErrorDetail

class UIUXEvaluator(BaseEvaluator):
    @property
    def name(self) -> str:
        return "UI/UX Evaluator"

    def evaluate(self, target_dir: Path) -> EvaluatorResult:
        errors = []
        extensions_to_check = {'.js', '.jsx', '.ts', '.tsx', '.html'}

        for path in target_dir.rglob('*'):
            if "tests" in path.parts and "dummy_codebases" not in path.parts:
                continue
            if path.is_file() and path.suffix in extensions_to_check:
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 1. Structural styling flaws: Catch inline styles (style={{...}} or style="...")
                    inline_style_pattern_react = re.compile(r"""style=\{\{.*?\}\}""", re.DOTALL)
                    for match in inline_style_pattern_react.finditer(content):
                        errors.append(ErrorDetail(
                            file=str(path),
                            line=content[:match.start()].count('\n') + 1,
                            issue="Inline styles",
                            title="Inline style object detected",
                            description="Inline style object detected (style={{...}}). Prefer CSS modules or styled-components.",
                            instructions="Extract inline styles to CSS modules or styled-components."
                        ))

                    inline_style_pattern_html = re.compile(r"""style=['"].*?['"]""", re.IGNORECASE)
                    for match in inline_style_pattern_html.finditer(content):
                        errors.append(ErrorDetail(
                            file=str(path),
                            line=content[:match.start()].count('\n') + 1,
                            issue="Inline styles",
                            title="Inline style attribute detected",
                            description=f"Inline style attribute detected: {match.group(0)}. Prefer external CSS.",
                            instructions="Extract inline styles to external CSS."
                        ))

                    # 2. Misconfigured production layout wrappers
                    if 'export default ' in content and ('return (' in content or 'return <' in content):
                        if not re.search(r"""<(Layout|Provider|AppProvider|ThemeProvider)\b""", content):
                            root_return_pattern = re.compile(r"""return\s*\(\s*<(div|main|section|article)\b""")
                            if root_return_pattern.search(content):
                                errors.append(ErrorDetail(
                                    file=str(path),
                                    line=0, # General file issue
                                    issue="Missing layout wrapper",
                                    title="Missing layout wrapper",
                                    description="Main component appears to return raw HTML elements without a top-level Layout or Provider wrapper.",
                                    instructions="Wrap the main component's return value in a top-level Layout or Provider wrapper."
                                ))

                except (OSError, PermissionError, UnicodeDecodeError) as e:
                    print(f"Error reading {path}: {e}")
                except Exception as e:
                    print(f"Unhandled error processing {path}: {e}")

        return EvaluatorResult(
            passed=len(errors) == 0,
            errors=errors
        )
