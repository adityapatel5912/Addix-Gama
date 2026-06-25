import os
import re

def evaluate(codebase_path):
    errors = []
    # Very basic static analysis to find broken connections
    # Look for patterns like db = "broken_connection:5432"
    broken_db_pattern = re.compile(r'db\s*=\s*["\']broken_connection.*?["\']')

    for root, _, files in os.walk(codebase_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if broken_db_pattern.search(content):
                        errors.append(f"Broken database connection found in {file_path}")

    return errors
