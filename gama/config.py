import pathlib
from typing import Optional
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class GamaConfig(BaseSettings):
    """
    Configuration for Gama engine.
    """
    openai_api_key: Optional[SecretStr] = Field(default=None, description="OpenAI API Key")
    anthropic_api_key: Optional[SecretStr] = Field(default=None, description="Anthropic API Key")
    gemini_api_key: Optional[SecretStr] = Field(default=None, description="Gemini API Key")

    workspace_path: pathlib.Path = Field(
        default=pathlib.Path("."),
        description="Path to the target project being audited"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

# Instantiate a global config object if needed, or keep it as class
# For now, just having the class fulfills the requirements.
