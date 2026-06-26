import os
import pytest
from gama.reporter import generate_audit_report

def test_generate_audit_report(tmp_path):
    # Dummy markdown content with headers, paragraphs, lists, and blockquotes
    markdown_content = """# Certification Report

## Introduction
This is a **test** report to certify the software codebase.

## Findings
The system identified the following structural elements:
- Database connectivity is solid.
- Authentication chains are valid.
- Security protocols active.
- UI/UX passes automated visual tests.

## Additional Details
1. Step one is verification.
2. Step two is certification.
3. Step three is deployment.

> This report is generated autonomously by Gama.

Code reference: `import gama`

End of report.
"""
    output_pdf = tmp_path / "test_report.pdf"

    # Generate the PDF
    generate_audit_report(markdown_content, str(output_pdf))

    # Assert PDF was created and has content
    assert os.path.exists(output_pdf)
    assert os.path.getsize(output_pdf) > 0
