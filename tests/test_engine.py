import os
import pytest
from gama.engine import scan

def test_engine_flags_clean_codebase():
    # Arrange
    clean_codebase_path = os.path.join(os.path.dirname(__file__), 'dummy_codebases', 'clean')

    # Act
    errors = scan(clean_codebase_path)

    # Assert
    assert len(errors) == 0, f"Expected 0 errors, but got {len(errors)}: {errors}"

def test_engine_flags_buggy_codebase():
    # Arrange
    buggy_codebase_path = os.path.join(os.path.dirname(__file__), 'dummy_codebases', 'buggy')

    # Act
    errors = scan(buggy_codebase_path)

    # Assert
    assert len(errors) == 2, f"Expected 2 errors, but got {len(errors)}: {errors}"

    # Verify specific errors were flagged
    assert any("Hardcoded password found" in error for error in errors)
    assert any("Broken database connection found" in error for error in errors)
