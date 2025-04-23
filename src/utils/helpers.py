import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

def setup_logging(log_config: Dict[str, Any]) -> None:
    """Configure logging based on provided configuration."""
    logging.basicConfig(
        level=log_config["level"],
        format=log_config["format"],
        filename=log_config["file"]
    )

def load_json_file(file_path: Path) -> Dict[str, Any]:
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON file {file_path}: {str(e)}")
        raise

def save_json_file(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.error(f"Error saving JSON file {file_path}: {str(e)}")
        raise

def generate_output_filename(category: str, format_type: str) -> str:
    """Generate a standardized output filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{category}_{timestamp}.{format_type}"

def validate_case_data(data: Dict[str, Any]) -> bool:
    """Validate case study data structure."""
    required_fields = ["title", "description", "category", "stakeholders"]
    return all(field in data for field in required_fields)

def format_deliberation_output(content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Format deliberation output with metadata."""
    return {
        "content": content,
        "metadata": metadata or {},
        "timestamp": datetime.now().isoformat()
    } 