import os
import re

def evaluate(codebase_path):
    errors = []
    # Very basic static analysis to find hardcoded passwords
    # Look for patterns like password = "..." or password='...'
    password_pattern = re.compile(r'password\s*=\s*["\'][^"\']+["\']')

    for root, _, files in os.walk(codebase_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if password_pattern.search(content):
                        errors.append(f"Hardcoded password found in {file_path}")

    return errors
