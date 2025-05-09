"""
Unified API client for ConsultAI.
This module provides a centralized interface for making API requests,
including parallel request handling and performance monitoring.
"""

import os
import time
import asyncio
import logging
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime
import aiohttp
from openai import AsyncOpenAI, OpenAI

from consultai.config.config import (
    get_api_config,
    get_token_config,
    get_metrics_config
)
from consultai.utils.request_confirmation import RequestConfirmation

# Configure logging
logger = logging.getLogger(__name__)

class APIClient:
    """
    Unified API client for making requests to OpenAI and other LLM providers.
    Supports both synchronous and asynchronous operations, as well as parallel requests.
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None, 
        base_url: Optional[str] = None,
        max_concurrent: int = 3,
        require_confirmation: bool = False
    ):
        """
        Initialize the API client.
        
        Args:
            api_key: OpenAI API key (optional, will use from config if not provided)
            base_url: Base URL for API (optional, will use from config if not provided)
            max_concurrent: Maximum number of concurrent requests
            require_confirmation: Whether to require confirmation before making requests
        """
        # Get configuration
        self.api_config = get_api_config()
        self.token_config = get_token_config()
        self.metrics_config = get_metrics_config()
        
        # Use provided credentials or fall back to config
        self.api_key = api_key or self.api_config["api_key"]
        self.base_url = base_url or self.api_config["base_url"]
        
        # Clean up base_url (remove any extra spaces or comments)
        self.base_url = self.base_url.split("#")[0].strip()
        
        self.max_concurrent = max_concurrent
        self.require_confirmation = require_confirmation
        
        # Initialize clients
        self.sync_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.async_client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # Initialize request confirmation if needed
        if self.require_confirmation:
            self.confirmation = RequestConfirmation(api_key=self.api_key, base_url=self.base_url)
        
        # Performance tracking
        self.request_times = []
        self.request_counts = 0
        self.error_counts = 0
        
        # Semaphore for rate limiting
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
    
    def _prepare_request_details(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        file_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Prepare request details for confirmation.
        
        Args:
            prompt: The prompt to send to the API
            system_message: Optional system message to guide the model
            model: Model to use (optional, will use from config if not provided)
            temperature: Temperature setting (optional, will use from config if not provided)
            max_tokens: Maximum tokens to generate (optional, will use from config if not provided)
            file_path: Optional path to a file to include in the request
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Dictionary containing request details
        """
        # Use provided parameters or fall back to config
        model = model or self.api_config["model_name"]
        temperature = temperature if temperature is not None else self.api_config["temperature"]
        max_tokens = max_tokens or self.api_config["max_tokens"]
        
        # Prepare messages
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        # Estimate token usage
        estimated_tokens = self._estimate_token_usage(messages, max_tokens)
        
        # Prepare request details
        request_details = {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": messages,
            "estimated_tokens": estimated_tokens,
            "prompt": prompt,
            **kwargs
        }
        
        # Add file path if provided
        if file_path:
            request_details["file_path"] = file_path
        
        return request_details
    
    def _estimate_token_usage(self, messages: List[Dict[str, str]], max_tokens: int) -> int:
        """
        Estimate token usage for a request.
        
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens to generate
            
        Returns:
            Estimated token usage
        """
        # Simple estimation based on character count
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        estimated_input_tokens = total_chars // 4  # Rough estimate: 4 chars per token
        
        # Add output tokens
        estimated_output_tokens = max_tokens
        
        return estimated_input_tokens + estimated_output_tokens
    
    def _process_response(self, response: Any, start_time: float) -> Dict[str, Any]:
        """
        Process API response and extract relevant information.
        
        Args:
            response: The API response
            start_time: Start time of the request
            
        Returns:
            Dictionary containing processed response data
        """
        # Calculate response time
        end_time = time.time()
        response_time = end_time - start_time
        self.request_times.append(response_time)
        self.request_counts += 1
        
        # Extract content
        content = response.choices[0].message.content
        
        # Calculate token usage
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        
        # Calculate cost
        input_cost = input_tokens * self.token_config[response.model]["input_token_cost"]
        output_cost = output_tokens * self.token_config[response.model]["output_token_cost"]
        total_cost = input_cost + output_cost
        
        return {
            "content": content,
            "response_time": response_time,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "error": None
        }
    
    def _handle_error(self, error: Exception, start_time: float) -> Dict[str, Any]:
        """
        Handle API request error.
        
        Args:
            error: The exception that occurred
            start_time: Start time of the request
            
        Returns:
            Dictionary containing error information
        """
        # Calculate response time for failed request
        end_time = time.time()
        response_time = end_time - start_time
        self.request_times.append(response_time)
        self.request_counts += 1
        self.error_counts += 1
        
        return {
            "content": f"[Error: {str(error)}]",
            "response_time": response_time,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "input_cost": 0,
            "output_cost": 0,
            "total_cost": 0,
            "error": str(error)
        }
    
    def generate_response(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        file_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the OpenAI API (synchronous).
        
        Args:
            prompt: The prompt to send to the API
            system_message: Optional system message to guide the model
            model: Model to use (optional, will use from config if not provided)
            temperature: Temperature setting (optional, will use from config if not provided)
            max_tokens: Maximum tokens to generate (optional, will use from config if not provided)
            file_path: Optional path to a file to include in the request
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Prepare request details
        request_details = self._prepare_request_details(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            file_path=file_path,
            **kwargs
        )
        
        # Check if confirmation is required
        if self.require_confirmation:
            confirmed = self.confirmation.confirm_request(request_details)
            self.confirmation.log_request(request_details, confirmed)
            
            if not confirmed:
                return {
                    "content": "Request cancelled by user",
                    "response_time": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "input_cost": 0,
                    "output_cost": 0,
                    "total_cost": 0,
                    "error": "Request cancelled by user"
                }
        
        # Track start time
        start_time = time.time()
        
        # Make API request with retries
        for attempt in range(self.api_config["max_retries"]):
            try:
                response = self.sync_client.chat.completions.create(
                    model=request_details["model"],
                    messages=request_details["messages"],
                    temperature=request_details["temperature"],
                    max_tokens=request_details["max_tokens"],
                    **kwargs
                )
                return self._process_response(response, start_time)
                
            except Exception as e:
                logger.error(f"Error generating response (attempt {attempt + 1}): {str(e)}")
                if attempt < self.api_config["max_retries"] - 1:
                    time.sleep(self.api_config["retry_delay"])
                else:
                    return self._handle_error(e, start_time)
    
    async def generate_response_async(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        file_path: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response using the OpenAI API (asynchronous).
        
        Args:
            prompt: The prompt to send to the API
            system_message: Optional system message to guide the model
            model: Model to use (optional, will use from config if not provided)
            temperature: Temperature setting (optional, will use from config if not provided)
            max_tokens: Maximum tokens to generate (optional, will use from config if not provided)
            file_path: Optional path to a file to include in the request
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Prepare request details
        request_details = self._prepare_request_details(
            prompt, system_message, model, temperature, max_tokens, file_path, **kwargs
        )
        
        # Check if we're in mock mode
        if self.api_config.get("mock_mode", False):
            logger.info("Mock mode enabled, returning mock response")
            # Create a mock response
            return {
                "content": f"Mock response for: {prompt[:50]}...",
                "response_time": 0.1,
                "input_tokens": 10,
                "output_tokens": 20,
                "total_tokens": 30,
                "input_cost": 0.0,
                "output_cost": 0.0,
                "total_cost": 0.0,
                "error": None
            }
        
        # Get confirmation if required
        if self.require_confirmation:
            self.confirmation.confirm_request(request_details)
        
        # Prepare messages
        messages = [{"role": m["role"], "content": m["content"]} for m in request_details["messages"]]
        
        # Set up retry logic
        max_retries = self.api_config["max_retries"]
        retry_delay = self.api_config["retry_delay"]
        
        # Filter out parameters that should not be passed to the API
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in [
            'api_key', 'base_url', 'max_concurrent', 'require_confirmation', 'messages', 'estimated_tokens'
        ]}
        
        # Call API with retries
        start_time = time.time()
        for attempt in range(max_retries):
            try:
                # Make API call with correctly formatted parameters
                response = await self.async_client.chat.completions.create(
                    model=request_details["model"],
                    messages=messages,
                    temperature=request_details["temperature"],
                    max_tokens=request_details["max_tokens"],
                    **filtered_kwargs
                )
                
                # Process and return response
                return self._process_response(response, start_time)
            except Exception as e:
                # Log error
                logger.error(f"Error generating response (attempt {attempt + 1}): {str(e)}")
                
                # If this is the last attempt, return error
                if attempt == max_retries - 1:
                    return self._handle_error(e, start_time)
                
                # Otherwise, wait before retrying
                await asyncio.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
    
    async def make_parallel_requests(
        self,
        prompts: List[str],
        system_messages: Optional[List[Optional[str]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        file_paths: Optional[List[Optional[str]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Make multiple API requests in parallel.
        
        Args:
            prompts: List of prompts to send
            system_messages: Optional list of system messages (one per prompt)
            model: Model to use (optional, will use from config if not provided)
            temperature: Temperature setting (optional, will use from config if not provided)
            max_tokens: Maximum tokens to generate (optional, will use from config if not provided)
            file_paths: Optional list of file paths (one per prompt)
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            List of response dictionaries
        """
        # Prepare request details for each prompt
        request_details_list = []
        for i, prompt in enumerate(prompts):
            system_message = system_messages[i] if system_messages and i < len(system_messages) else None
            file_path = file_paths[i] if file_paths and i < len(file_paths) else None
            
            request_details = self._prepare_request_details(
                prompt=prompt,
                system_message=system_message,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                file_path=file_path,
                **kwargs
            )
            request_details_list.append(request_details)
        
        # Check if confirmation is required
        if self.require_confirmation:
            # Display all requests and ask for confirmation
            print("\n" + "=" * 80)
            print(f"CONFIRM {len(request_details_list)} PARALLEL API REQUESTS")
            print("=" * 80)
            
            for i, details in enumerate(request_details_list):
                print(f"\nREQUEST {i+1}:")
                print(self.confirmation._format_request_details(details))
            
            print("=" * 80)
            
            # Ask for confirmation
            while True:
                response = input("\nProceed with these requests? (y/n): ").lower()
                if response in ['y', 'yes']:
                    break
                elif response in ['n', 'no']:
                    # Return cancelled responses
                    return [{
                        "content": "Request cancelled by user",
                        "response_time": 0,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "total_tokens": 0,
                        "input_cost": 0,
                        "output_cost": 0,
                        "total_cost": 0,
                        "error": "Request cancelled by user"
                    } for _ in range(len(prompts))]
                else:
                    print("Please enter 'y' or 'n'.")
            
            # Log the requests
            for details in request_details_list:
                self.confirmation.log_request(details, True)
        
        # Prepare tasks
        tasks = []
        for details in request_details_list:
            task = self.generate_response_async(
                prompt=details["prompt"],
                system_message=details["messages"][0]["content"] if details["messages"] and details["messages"][0]["role"] == "system" else None,
                model=details["model"],
                temperature=details["temperature"],
                max_tokens=details["max_tokens"],
                **{k: v for k, v in details.items() if k not in ["prompt", "messages", "model", "temperature", "max_tokens", "estimated_tokens", "file_path"]}
            )
            tasks.append(task)
        
        # Execute tasks in parallel
        return await asyncio.gather(*tasks)
    
    def run_parallel_requests_sync(
        self,
        prompts: List[str],
        system_messages: Optional[List[Optional[str]]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        file_paths: Optional[List[Optional[str]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Synchronous wrapper for making parallel requests.
        
        Args:
            prompts: List of prompts to send
            system_messages: Optional list of system messages (one per prompt)
            model: Model to use (optional, will use from config if not provided)
            temperature: Temperature setting (optional, will use from config if not provided)
            max_tokens: Maximum tokens to generate (optional, will use from config if not provided)
            file_paths: Optional list of file paths (one per prompt)
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            List of response dictionaries
        """
        return asyncio.run(self.make_parallel_requests(
            prompts=prompts,
            system_messages=system_messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            file_paths=file_paths,
            **kwargs
        ))
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for API requests.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.request_times:
            return {
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "total_requests": 0,
                "error_rate": 0,
                "total_tokens": 0,
                "total_cost": 0
            }
        
        return {
            "avg_response_time": sum(self.request_times) / len(self.request_times),
            "min_response_time": min(self.request_times),
            "max_response_time": max(self.request_times),
            "total_requests": self.request_counts,
            "error_rate": self.error_counts / self.request_counts if self.request_counts > 0 else 0,
            "total_tokens": sum(time * 100 for time in self.request_times),  # Rough estimate
            "total_cost": sum(time * 0.01 for time in self.request_times)  # Rough estimate
        }
    
    def estimate_cost(
        self,
        num_calls: int,
        avg_input_tokens: Optional[int] = None,
        avg_output_tokens: Optional[int] = None,
        model: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Estimate the cost for a given number of API calls.
        
        Args:
            num_calls: Number of API calls to estimate
            avg_input_tokens: Average input tokens per call (optional)
            avg_output_tokens: Average output tokens per call (optional)
            model: Model to use for estimation (optional)
            
        Returns:
            Dictionary with cost estimates
        """
        # Use provided parameters or fall back to config
        model = model or self.api_config["model_name"]
        avg_input_tokens = avg_input_tokens or self.token_config["estimated_input_tokens_per_message"]
        avg_output_tokens = avg_output_tokens or self.token_config["estimated_output_tokens_per_response"]
        
        # Calculate costs
        input_cost = num_calls * avg_input_tokens * self.token_config[model]["input_token_cost"]
        output_cost = num_calls * avg_output_tokens * self.token_config[model]["output_token_cost"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost_usd": input_cost,
            "output_cost_usd": output_cost,
            "total_cost_usd": total_cost,
            "estimated_tokens": num_calls * (avg_input_tokens + avg_output_tokens)
        }

    async def make_request(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Wrapper for generate_response_async to maintain backward compatibility.
        
        Args:
            prompt: The prompt to send to the API
            system_message: Optional system message to guide the model
            model: Model to use (optional, will use from config if not provided)
            temperature: Temperature setting (optional, will use from config if not provided)
            max_tokens: Maximum tokens to generate (optional, will use from config if not provided)
            **kwargs: Additional arguments to pass to the API
            
        Returns:
            Dictionary containing the response and metadata
        """
        return await self.generate_response_async(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        ) 