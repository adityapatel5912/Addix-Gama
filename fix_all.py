import os
import re

def fix_file(filepath):
    if not os.path.exists(filepath): return
    with open(filepath, 'r') as f:
        content = f.read()

    # Add logging import and logger setup if not exists
    if 'logger = logging.getLogger(__name__)' not in content:
        # find the last import
        lines = content.split('\n')
        last_import = -1
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import = i

        logger_setup = [
            "",
            "import logging",
            "logger = logging.getLogger(__name__)",
            "logger.setLevel(logging.INFO)",
            "if not logger.handlers:",
            "    handler = logging.StreamHandler()",
            "    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')",
            "    handler.setFormatter(formatter)",
            "    logger.addHandler(handler)",
            ""
        ]

        lines.insert(last_import + 1, '\n'.join(logger_setup))
        content = '\n'.join(lines)

    # replace print with logger
    content = content.replace('print(f"Error', 'logger.error(f"Error')
    content = content.replace('print(f"Unhandled', 'logger.error(f"Unhandled')
    content = content.replace('print(f"Watching', 'logger.info(f"Watching')
    content = content.replace('print("Change detected', 'logger.info("Change detected')
    content = content.replace('print("Resuming loop', 'logger.info("Resuming loop')
    content = content.replace('print("Evaluating project', 'logger.info("Evaluating project')
    content = content.replace('print("No failures detected', 'logger.info("No failures detected')
    content = content.replace('print("Failures detected', 'logger.info("Failures detected')
    content = content.replace('print(f"State file written', 'logger.info(f"State file written')

    with open(filepath, 'w') as f:
        f.write(content)

for root, _, files in os.walk('gama'):
    for f in files:
        if f.endswith('.py'):
            fix_file(os.path.join(root, f))
