"""
Enhanced Agent Module for ConsultAI.
This module provides advanced agent implementations with improved capabilities.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import time

from consultai.utils.api_client import APIClient
from consultai.config.config import get_agents_config, get_api_config

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedAgent:
    """An enhanced agent with specialized capabilities for ethical deliberation."""
    
    def __init__(
        self,
        role: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4.1-2025-04-14",
        require_confirmation: bool = True
    ):
        """
        Initialize an enhanced agent.
        
        Args:
            role: The role/perspective this agent represents
            api_key: Optional API key override
            base_url: Optional base URL override
            model: Model to use for agent responses (default: gpt-4.1-2025-04-14)
            require_confirmation: Whether to require confirmation for API calls
        """
        # Get configuration
        self.agent_config = get_agents_config()
        self.api_config = get_api_config()
        
        # Initialize agent properties
        self.role = role
        self.memory_size = 10  # Default memory_size
        self.max_tokens = self.api_config["max_tokens"]  # Default max_tokens
        self.require_confirmation = require_confirmation
        
        # Initialize API client with explicit configuration
        # Always set require_confirmation to False to avoid multiple confirmations
        self.api_client = APIClient(
            api_key=api_key or self.api_config["api_key"],
            base_url=base_url or self.api_config["base_url"],
            require_confirmation=False  # Always set to False to avoid multiple confirmations
        )
        
        # Initialize memory and tracking
        self.memories = []
        self.innovation_tracker = InnovationTracker()
    
    def generate_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate a response using the enhanced agent.
        
        Args:
            prompt: The prompt to send to the API
            context: Optional context information
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Create enhanced prompt
        enhanced_prompt = self._create_enhanced_prompt(prompt, context)
        
        # Get system message for role
        system_message = self.agent_config["roles"][self.role]["system_message"]
        
        # Generate response
        response = self._call_llm(enhanced_prompt, system_message)
        
        # Update memory and track innovation
        self._update_memory(prompt, response["content"])
        self.innovation_tracker.track_response(response["content"])
        
        return response
    
    def _create_enhanced_prompt(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an enhanced prompt with memory and context.
        
        Args:
            prompt: The base prompt
            context: Optional context information
            
        Returns:
            Enhanced prompt string
        """
        # Format conversation history
        history = self._format_conversation_history()
        
        # Format relevant memories
        memories = self._format_relevant_memories(prompt)
        
        # Format context
        context_str = self._format_context(context) if context else ""
        
        # Combine all components
        enhanced_prompt = f"""Role: {self.role}

{context_str}

Previous Conversation:
{history}

Relevant Memories:
{memories}

Current Task:
{prompt}

Please provide a response that:
1. Addresses the current task
2. References relevant memories if applicable
3. Maintains consistency with previous conversation
4. Demonstrates innovative thinking"""
        
        return enhanced_prompt
    
    def _format_conversation_history(self) -> str:
        """
        Format the conversation history for inclusion in prompts.
        
        Returns:
            Formatted conversation history string
        """
        if not self.memories:
            return "No previous conversation."
        
        history_text = ""
        for memory in self.memories[-5:]:  # Last 5 memories
            history_text += f"{memory['role']}: {memory['content']}\n\n"
        
        return history_text
    
    def _format_relevant_memories(self, prompt: str) -> str:
        """
        Format relevant memories for the current prompt.
        
        Args:
            prompt: The current prompt
            
        Returns:
            Formatted relevant memories string
        """
        if not self.memories:
            return "No relevant memories."
        
        # Simple relevance scoring based on keyword matching
        relevant_memories = []
        prompt_keywords = set(prompt.lower().split())
        
        for memory in self.memories:
            memory_keywords = set(memory["content"].lower().split())
            relevance = len(prompt_keywords.intersection(memory_keywords)) / len(prompt_keywords)
            
            if relevance > 0.3:  # 30% keyword overlap threshold
                relevant_memories.append((memory, relevance))
        
        # Sort by relevance
        relevant_memories.sort(key=lambda x: x[1], reverse=True)
        
        # Format top 3 most relevant memories
        memories_text = ""
        for memory, _ in relevant_memories[:3]:
            memories_text += f"- {memory['content']}\n"
        
        return memories_text if memories_text else "No relevant memories found."
    
    def _format_context(self, context: Optional[Dict[str, Any]]) -> str:
        """
        Format context information for inclusion in prompts.
        
        Args:
            context: Context information
            
        Returns:
            Formatted context string
        """
        if not context:
            return ""
        
        context_text = "Context:\n"
        for key, value in context.items():
            context_text += f"- {key}: {value}\n"
        
        return context_text
    
    def _call_llm(self, prompt: str, system_message: str) -> Dict[str, Any]:
        """
        Call the language model with the enhanced prompt.
        
        Args:
            prompt: The enhanced prompt
            system_message: The system message
            
        Returns:
            Dictionary containing the response and metadata
        """
        return self.api_client.generate_response(
            prompt=prompt,
            system_message=system_message,
            max_tokens=self.max_tokens
        )
    
    def _update_memory(self, prompt: str, response: str) -> None:
        """
        Update the agent's memory with new information.
        
        Args:
            prompt: The prompt that was sent
            response: The response that was received
        """
        # Add new memories
        self.memories.append({
            "role": "user",
            "content": prompt,
            "timestamp": time.time(),
            "importance": self._calculate_importance(prompt)
        })
        
        self.memories.append({
            "role": "assistant",
            "content": response,
            "timestamp": time.time(),
            "importance": self._calculate_importance(response)
        })
        
        # Trim memories if needed
        if len(self.memories) > self.memory_size * 2:  # *2 because each interaction has 2 memories
            # Sort by importance and timestamp
            self.memories.sort(key=lambda x: (x["importance"], x["timestamp"]), reverse=True)
            self.memories = self.memories[:self.memory_size * 2]
            # Sort back by timestamp
            self.memories.sort(key=lambda x: x["timestamp"])
    
    def _calculate_importance(self, text: str) -> float:
        """
        Calculate the importance of a memory.
        
        Args:
            text: The text to evaluate
            
        Returns:
            Importance score between 0 and 1
        """
        # Simple importance calculation based on length and keyword presence
        importance = min(len(text) / 1000, 1.0)  # Length factor
        
        # Add importance for key terms
        key_terms = ["important", "critical", "key", "essential", "crucial"]
        for term in key_terms:
            if term in text.lower():
                importance += 0.2
        
        return min(importance, 1.0)
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics for the agent.
        
        Returns:
            Dictionary containing performance metrics
        """
        # Get API client metrics
        api_metrics = self.api_client.get_performance_stats()
        
        # Get innovation metrics
        innovation_metrics = self.innovation_tracker.get_metrics()
        
        return {
            "api_metrics": api_metrics,
            "innovation_metrics": innovation_metrics,
            "memory_size": len(self.memories),
            "role": self.role
        }

class InnovationTracker:
    """
    Tracks innovation metrics for agent responses.
    """
    
    def __init__(self):
        """
        Initialize the innovation tracker.
        """
        self.responses = []
        self.concept_scores = []
        self.solution_scores = []
        self.approach_scores = []
    
    def track_response(self, response: str) -> None:
        """
        Track a new response and calculate innovation scores.
        
        Args:
            response: The response to track
        """
        # Store response
        self.responses.append({
            "content": response,
            "timestamp": time.time()
        })
        
        # Calculate innovation scores
        self.concept_scores.append(self._calculate_concept_score(response))
        self.solution_scores.append(self._calculate_solution_score(response))
        self.approach_scores.append(self._calculate_approach_score(response))
    
    def _calculate_concept_score(self, response: str) -> float:
        """
        Calculate the concept uniqueness score.
        
        Args:
            response: The response to evaluate
            
        Returns:
            Score between 0 and 1
        """
        # Simple implementation - can be enhanced with more sophisticated analysis
        unique_words = set(response.lower().split())
        total_words = len(unique_words)
        
        if not self.responses:
            return 1.0
        
        # Compare with previous responses
        previous_words = set()
        for prev_response in self.responses:
            previous_words.update(prev_response["content"].lower().split())
        
        new_words = len(unique_words - previous_words)
        return min(new_words / total_words if total_words > 0 else 0, 1.0)
    
    def _calculate_solution_score(self, response: str) -> float:
        """
        Calculate the solution originality score.
        
        Args:
            response: The response to evaluate
            
        Returns:
            Score between 0 and 1
        """
        # Simple implementation - can be enhanced with more sophisticated analysis
        solution_indicators = ["solution", "approach", "method", "strategy", "technique"]
        has_solution = any(indicator in response.lower() for indicator in solution_indicators)
        
        if not has_solution:
            return 0.0
        
        # Calculate score based on solution description length
        solution_length = len(response)
        return min(solution_length / 1000, 1.0)
    
    def _calculate_approach_score(self, response: str) -> float:
        """
        Calculate the approach innovation score.
        
        Args:
            response: The response to evaluate
            
        Returns:
            Score between 0 and 1
        """
        # Simple implementation - can be enhanced with more sophisticated analysis
        innovation_indicators = ["innovative", "creative", "novel", "unique", "original"]
        has_innovation = any(indicator in response.lower() for indicator in innovation_indicators)
        
        if not has_innovation:
            return 0.0
        
        # Calculate score based on innovation description length
        innovation_length = len(response)
        return min(innovation_length / 1000, 1.0)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get innovation metrics.
        
        Returns:
            Dictionary containing innovation metrics
        """
        if not self.responses:
            return {
                "concept_uniqueness": 0.0,
                "solution_originality": 0.0,
                "approach_innovation": 0.0,
                "overall_score": 0.0
            }
        
        return {
            "concept_uniqueness": sum(self.concept_scores) / len(self.concept_scores),
            "solution_originality": sum(self.solution_scores) / len(self.solution_scores),
            "approach_innovation": sum(self.approach_scores) / len(self.approach_scores),
            "overall_score": (
                sum(self.concept_scores) +
                sum(self.solution_scores) +
                sum(self.approach_scores)
            ) / (3 * len(self.responses))
        } 