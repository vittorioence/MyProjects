"""
Request confirmation module for ConsultAI.
This module provides functionality to display API request details and ask for confirmation before proceeding.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

from consultai.config.config import get_api_config, get_token_config

# Configure logging
logger = logging.getLogger(__name__)

class RequestConfirmation:
    """
    Handles confirmation of API requests before they are sent.
    Displays request details and asks for user confirmation.
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the request confirmation handler.
        
        Args:
            api_key: OpenAI API key (optional, will use from config if not provided)
            base_url: Base URL for API (optional, will use from config if not provided)
        """
        # Get configuration
        self.api_config = get_api_config()
        self.token_config = get_token_config()
        
        # Use provided credentials or fall back to config
        self.api_key = api_key or self.api_config["api_key"]
        self.base_url = base_url or self.api_config["base_url"]
        
        # Mask API key for display
        self.masked_api_key = self._mask_api_key(self.api_key)
    
    def _mask_api_key(self, api_key: str) -> str:
        """
        Mask the API key for display purposes.
        
        Args:
            api_key: The API key to mask
            
        Returns:
            Masked API key string
        """
        if not api_key:
            return "Not set"
        
        if len(api_key) <= 8:
            return "*" * len(api_key)
        
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format messages for display.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Formatted messages string
        """
        formatted = ""
        for i, msg in enumerate(messages):
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Truncate long content
            if len(content) > 100:
                content = content[:100] + "..."
            
            formatted += f"  {i+1}. {role.upper()}: {content}\n"
        
        return formatted
    
    def _format_file_content(self, file_path: str, max_lines: int = 10) -> str:
        """
        Format file content for display.
        
        Args:
            file_path: Path to the file
            max_lines: Maximum number of lines to display
            
        Returns:
            Formatted file content string
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if len(lines) <= max_lines:
                return "".join(lines)
            
            return "".join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
        
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def _format_request_details(self, request_details: Dict[str, Any]) -> str:
        """
        Format request details for display.
        
        Args:
            request_details: Dictionary of request details
            
        Returns:
            Formatted request details string
        """
        details = "REQUEST DETAILS:\n"
        details += f"  API Key: {self.masked_api_key}\n"
        details += f"  Base URL: {request_details.get('base_url', self.base_url)}\n"
        details += f"  Model: {request_details.get('model', self.api_config['model_name'])}\n"
        details += f"  Temperature: {request_details.get('temperature', self.api_config['temperature'])}\n"
        details += f"  Max Tokens: {request_details.get('max_tokens', self.api_config['max_tokens'])}\n"
        
        if 'messages' in request_details:
            details += "\nMESSAGES:\n"
            for i, msg in enumerate(request_details['messages']):
                role = msg.get("role", "user")
                content = msg.get("content", "")
                # Truncate content to 50 characters
                if len(content) > 50:
                    content = content[:50] + "..."
                details += f"  {i+1}. {role.upper()}: {content}\n"
        
        if 'file_path' in request_details:
            details += f"\nFILE: {request_details['file_path']}\n"
        
        if 'prompt' in request_details:
            details += "\nPROMPT:\n"
            prompt = request_details['prompt']
            # Truncate prompt to 50 characters
            if len(prompt) > 50:
                prompt = prompt[:50] + "..."
            details += f"  {prompt}\n"
        
        # Estimate cost
        if 'estimated_tokens' in request_details:
            model = request_details.get('model', self.api_config['model_name'])
            
            # Get token costs from the token config
            model_config = self.token_config.get(model, {})
            input_cost_per_token = model_config.get('input', 0) / 1000  # Convert from per 1K tokens to per token
            output_cost_per_token = model_config.get('output', 0) / 1000  # Convert from per 1K tokens to per token
            
            # Calculate costs
            input_cost = request_details['estimated_tokens'] * input_cost_per_token
            output_cost = request_details['estimated_tokens'] * output_cost_per_token
            total_cost = input_cost + output_cost
            
            details += f"\nESTIMATED COST: ${total_cost:.4f}\n"
        
        return details
    
    def confirm_request(self, request_details: Dict[str, Any]) -> bool:
        """
        Display request details and ask for confirmation.
        
        Args:
            request_details: Dictionary of request details
            
        Returns:
            True if confirmed, False otherwise
        """
        # Format request details
        details = self._format_request_details(request_details)
        
        # Display request details
        print("\n" + "=" * 80)
        print("CONFIRM API REQUEST")
        print("=" * 80)
        print(details)
        print("=" * 80)
        
        # Ask for confirmation
        while True:
            response = input("\nProceed with this request? (y/n): ").lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def log_request(self, request_details: Dict[str, Any], confirmed: bool) -> None:
        """
        Log the request details and confirmation status.
        
        Args:
            request_details: Dictionary of request details
            confirmed: Whether the request was confirmed
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "api_key": self.masked_api_key,
            "base_url": request_details.get('base_url', self.base_url),
            "model": request_details.get('model', self.api_config['model_name']),
            "confirmed": confirmed,
            "request_details": {k: v for k, v in request_details.items() if k != 'api_key'}
        }
        
        logger.info(f"Request {'confirmed' if confirmed else 'rejected'}: {json.dumps(log_entry)}") 