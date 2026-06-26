import os
import pathlib

import pytest
from pydantic import SecretStr

from gama.config import GamaConfig


def test_default_config():
    config = GamaConfig()
    assert config.openai_api_key is None
    assert config.anthropic_api_key is None
    assert config.gemini_api_key is None
    assert config.workspace_path == pathlib.Path(".")


def test_config_with_env_vars(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-123")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-123")
    monkeypatch.setenv("WORKSPACE_PATH", "/tmp/project")

    config = GamaConfig()
    assert config.openai_api_key.get_secret_value() == "sk-123"
    assert config.anthropic_api_key.get_secret_value() == "sk-ant-123"
    assert config.workspace_path == pathlib.Path("/tmp/project")
    assert config.gemini_api_key is None
