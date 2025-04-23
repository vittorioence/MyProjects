from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# API Configuration
API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("OPENAI_BASE_URL")

# Model Configuration
MODEL_CONFIG: Dict[str, Any] = {
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2000,
    "top_p": 0.9,
}

# Case Study Categories
CASE_CATEGORIES = [
    "autonomy",
    "beneficence",
    "justice",
    "resource_allocation"
]

# Output Formats
OUTPUT_FORMATS = {
    "deliberation": "markdown",
    "evaluation": "json",
    "summary": "text"
}

# Logging Configuration
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": BASE_DIR / "logs" / "app.log"
} 