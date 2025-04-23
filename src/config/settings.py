import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL= os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# File Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Model Configuration
MODEL_CONFIG: Dict[str, Any] = {
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "2000")),
    "top_p": float(os.getenv("MODEL_TOP_P", "1.0")),
    "frequency_penalty": float(os.getenv("MODEL_FREQUENCY_PENALTY", "0.0")),
    "presence_penalty": float(os.getenv("MODEL_PRESENCE_PENALTY", "0.0"))
}

# Case Study Analysis Settings
CASE_ANALYSIS_CONFIG = {
    "max_retries": int(os.getenv("MAX_RETRIES", "3")),
    "retry_delay": int(os.getenv("RETRY_DELAY", "1")),  # seconds
    "timeout": int(os.getenv("REQUEST_TIMEOUT", "30"))  # seconds
}

def get_model_config() -> Dict[str, Any]:
    """Get the model configuration."""
    return MODEL_CONFIG.copy()

def validate_settings() -> bool:
    """Validate that all required settings are present."""
    required_settings = ["OPENAI_API_KEY"]
    return all(os.getenv(setting) for setting in required_settings) 