from typing import Dict, Any, List, Optional
import openai
from datetime import datetime
import time
import logging

from src.config.settings import (
    OPENAI_API_KEY,
    DEFAULT_MODEL,
    get_model_config,
    CASE_ANALYSIS_CONFIG
)
from src.utils.common import format_timestamp

# Configure logging
logger = logging.getLogger(__name__)

class OpenAIModel:
    """Concrete implementation of OpenAI GPT model."""
    
    def __init__(self, model_name: str = DEFAULT_MODEL):
        """Initialize the OpenAI model.
        
        Args:
            model_name: Name of the GPT model to use
        """
        self.model_name = model_name
        self.config = get_model_config()
        openai.api_key = OPENAI_API_KEY
        
    def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from the model.
        
        Args:
            prompt: The user prompt
            system_message: Optional system message to guide the model
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
            
        Returns:
            The model's response text
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        config = self.config.copy()
        if temperature is not None:
            config["temperature"] = temperature
        if max_tokens is not None:
            config["max_tokens"] = max_tokens
            
        for attempt in range(CASE_ANALYSIS_CONFIG["max_retries"]):
            try:
                response = openai.ChatCompletion.create(
                    model=self.model_name,
                    messages=messages,
                    **config
                )
                return response.choices[0].message.content
            except Exception as e:
                logger.error(f"Error generating response (attempt {attempt + 1}): {str(e)}")
                if attempt < CASE_ANALYSIS_CONFIG["max_retries"] - 1:
                    time.sleep(CASE_ANALYSIS_CONFIG["retry_delay"])
                else:
                    raise
                    
    def analyze_case_study(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a case study using the model.
        
        Args:
            case_data: Dictionary containing case study information
            
        Returns:
            Dictionary containing analysis results
        """
        system_message = """You are an expert business analyst. Analyze the provided case study 
        and provide insights on:
        1. Key challenges faced
        2. Solutions implemented
        3. Outcomes and results
        4. Lessons learned
        Be concise and focus on actionable insights."""
        
        prompt = f"""Please analyze the following case study:
        
        Company: {case_data.get('company_name', 'N/A')}
        Industry: {case_data.get('industry', 'N/A')}
        Challenge: {case_data.get('challenge', 'N/A')}
        Solution: {case_data.get('solution', 'N/A')}
        Results: {case_data.get('results', 'N/A')}
        """
        
        try:
            analysis = self.generate_response(prompt, system_message)
            return {
                "timestamp": format_timestamp(),
                "case_id": case_data.get("case_id", "unknown"),
                "analysis": analysis,
                "model_used": self.model_name
            }
        except Exception as e:
            logger.error(f"Error analyzing case study: {str(e)}")
            raise 