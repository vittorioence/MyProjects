import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {str(e)}")
        raise

def save_json(data: Dict[str, Any], file_path: str) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving JSON to {file_path}: {str(e)}")
        raise

def load_json(file_path: str) -> Dict[str, Any]:
    """Load data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading JSON from {file_path}: {str(e)}")
        raise

def format_timestamp(timestamp: Optional[datetime] = None) -> str:
    """Format a timestamp for logging and file naming."""
    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime("%Y%m%d_%H%M%S")

def validate_case_data(case_data: Dict[str, Any]) -> bool:
    """Validate case study data structure."""
    required_fields = ["id", "content", "timestamp"]
    return all(field in case_data for field in required_fields)

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename 