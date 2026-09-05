"""
Recoup Agent Service — Configuration.

All settings loaded from environment variables via Pydantic Settings.
Model IDs are single constants — swap with a one-line change.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_ENV = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # --- Razorpay (Test Mode) ---
    razorpay_key_id: str = Field(default="", description="Razorpay test-mode Key ID")
    razorpay_key_secret: str = Field(default="", description="Razorpay test-mode Key Secret")
    razorpay_webhook_secret: str = Field(default="", description="Razorpay webhook secret for signature verification")

    # --- Groq (Primary LLM — speed-optimized) ---
    groq_api_key: str = Field(default="", description="Groq API key")
    groq_model_id: str = Field(default="openai/gpt-oss-120b", description="Groq model for classification + drafting")
    groq_whisper_model_id: str = Field(default="whisper-large-v3-turbo", description="Groq Whisper model for STT")

    # --- Google Gemini (Fallback LLM) ---
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model_id: str = Field(default="gemini-2.5-flash", description="Gemini model ID (fallback)")

    # --- Agent Configuration ---
    human_approval_threshold_inr: float = Field(default=5000.0, description="₹ threshold above which human approval is required")
    max_retry_attempts: int = Field(default=3, description="Max recovery retry attempts per case")
    dnd_start_hour: int = Field(default=21, description="Do-not-disturb start hour (IST, 24h)")
    dnd_end_hour: int = Field(default=8, description="Do-not-disturb end hour (IST, 24h)")

    # --- Database ---
    database_url: str = Field(default="sqlite:///./recoup.db", description="SQLite database URL")

    # --- Server ---
    agent_service_host: str = Field(default="0.0.0.0", description="Agent service host")
    agent_service_port: int = Field(default=8005, description="Agent service port")

    model_config = {
        "env_file": [str(ROOT_ENV), ".env"],
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


# Singleton — import this everywhere
settings = Settings()
