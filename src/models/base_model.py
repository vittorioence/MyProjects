from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseModel(ABC):
    """Abstract base class for AI model interactions."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the model with configuration."""
        self.config = config
        self.model_name = config.get("model_name", "default")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 1000)
        self.top_p = config.get("top_p", 1.0)
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model."""
        pass
    
    @abstractmethod
    async def analyze_case(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a case study and return insights."""
        pass
    
    def _format_prompt(self, template: str, **kwargs) -> str:
        """Format a prompt template with provided variables."""
        return template.format(**kwargs)
    
    def _validate_response(self, response: str) -> bool:
        """Validate the model's response."""
        return bool(response and len(response.strip()) > 0)
    
    def _extract_metadata(self, response: str) -> Dict[str, Any]:
        """Extract metadata from the model's response."""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        } 