"""
Deliberation module for ConsultAI.
This module handles the deliberation process with multiple agents using parallel API requests.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from consultai.utils.api_client import APIClient
from consultai.models.enhanced_agents import EnhancedAgent
from consultai.config.config import get_deliberation_config, get_api_config
from consultai.config.model_manager import ModelTier

# Configure logging
logger = logging.getLogger(__name__)

class DeliberationManager:
    """
    Manages the deliberation process with multiple agents.
    Handles parallel API requests and agent coordination.
    """
    
    def __init__(
        self,
        case_study: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4.1-2025-04-14",
        max_concurrent: int = 3,
        require_confirmation: bool = True
    ):
        """
        Initialize the deliberation manager.
        
        Args:
            case_study: The case study text to deliberate on
            api_key: OpenAI API key (optional, will use from config if not provided)
            base_url: Base URL for API (optional, will use from config if not provided)
            model: Model to use for deliberation (default: gpt-4.1-2025-04-14)
            max_concurrent: Maximum number of concurrent API requests
            require_confirmation: Whether to require confirmation before making API requests
        """
        # Get configuration
        self.config = get_deliberation_config()
        self.api_config = get_api_config()
        
        # Set properties
        self.case_study = case_study
        self.max_concurrent = max_concurrent
        self.model = model
        self.require_confirmation = require_confirmation
        
        # Initialize properties
        self.agents = []
        self.conversation_history = []
        self.consensus_reached = False
        self.confidence_tracker = {}  # Initialize confidence tracker
        
        # Initialize API client with explicit configuration
        # Pass require_confirmation=False to child components to avoid multiple confirmations
        self.api_client = APIClient(
            api_key=api_key or self.api_config["api_key"],
            base_url=base_url or self.api_config["base_url"],
            require_confirmation=False  # Always set to False to avoid multiple confirmations
        )
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self) -> List[EnhancedAgent]:
        """
        Initialize the agents for deliberation.
        
        Returns:
            List of initialized EnhancedAgent instances
        """
        self.agents = []
        for role, config in self.config["roles"].items():
            agent = EnhancedAgent(
                role=role,
                api_key=self.api_client.api_key,
                base_url=self.api_client.base_url,
                model=self.model,
                require_confirmation=self.require_confirmation
            )
            self.agents.append(agent)
        return self.agents
    
    async def run_deliberation(self, max_rounds: int = 5) -> Dict[str, Any]:
        """
        Run the deliberation process with parallel agent responses.
        
        Args:
            max_rounds: Maximum number of deliberation rounds
            
        Returns:
            Dictionary containing deliberation results and metrics
        """
        logger.info("Starting deliberation process")
        
        # Initialize results
        results = {
            "case_study": self.case_study,
            "start_time": datetime.now().isoformat(),
            "rounds": [],
            "final_consensus": None,
            "performance_metrics": {}
        }
        
        # Run deliberation rounds
        for round_num in range(max_rounds):
            logger.info(f"Starting round {round_num + 1}")
            
            # Get speaking agents
            speaking_agents = self._get_speaking_agents()
            
            # Run parallel agent responses
            round_results = await self._run_parallel_agent_responses(speaking_agents)
            
            # Update conversation state
            self._update_conversation_state(round_results)
            
            # Check for consensus
            if self._check_consensus():
                self.consensus_reached = True
                break
            
            # Add round results
            results["rounds"].append(round_results)
        
        # Generate final results
        results["end_time"] = datetime.now().isoformat()
        results["final_consensus"] = await self._generate_final_consensus()
        results["performance_metrics"] = self._get_performance_metrics()
        
        return results
    
    def _get_speaking_agents(self) -> List[EnhancedAgent]:
        """
        Determine which agents should speak in the current round.
        
        Returns:
            List of agents that should speak
        """
        # Simple round-robin selection
        start_idx = 0
        speaking_agents = []
        
        for i in range(min(self.max_concurrent, len(self.agents))):
            agent_idx = (start_idx + i) % len(self.agents)
            speaking_agents.append(self.agents[agent_idx])
        
        return speaking_agents
    
    async def _run_parallel_agent_responses(
        self,
        agents: List[EnhancedAgent]
    ) -> List[Dict[str, Any]]:
        """
        Run parallel API calls for multiple agents.
        
        Args:
            agents: List of agents to get responses from
            
        Returns:
            List of response dictionaries containing agent, response, and performance info
        """
        # Create prompts for each agent
        prompts = []
        for agent in agents:
            prompt = self._create_agent_prompt(agent)
            prompts.append(prompt)
        
        # Run parallel API calls
        responses = await self.api_client.make_parallel_requests(prompts)
        
        # Process responses
        results = []
        for agent, response in zip(agents, responses):
            results.append({
                "agent": agent,
                "response": response.get("content", ""),
                "performance": response.get("performance", {})
            })
        
        return results
    
    def _create_agent_prompt(self, agent: EnhancedAgent) -> str:
        """
        Create a prompt for an agent based on the current state.
        
        Args:
            agent: The agent to create a prompt for
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Case Study:
{self.case_study}

Current Conversation History:
{self._format_conversation_history()}

As a {agent.role}, please provide your perspective on the ethical considerations in this case.
Consider:
1. Key ethical principles involved
2. Potential conflicts or tensions
3. Possible approaches or solutions
4. Your confidence in your assessment

Please structure your response clearly and reference specific aspects of the case study."""
        
        return prompt
    
    def _format_conversation_history(self) -> str:
        """
        Format the conversation history for inclusion in prompts.
        
        Returns:
            Formatted conversation history string
        """
        if not self.conversation_history:
            return "No previous conversation."
        
        history_text = ""
        for entry in self.conversation_history[-5:]:  # Last 5 entries
            history_text += f"{entry['agent']}: {entry['content']}\n\n"
        
        return history_text
    
    def _update_conversation_state(self, round_results: Dict[str, Any]) -> None:
        """
        Update the conversation state with new responses.
        
        Args:
            round_results: Results from the current round
        """
        # Add new entries to conversation history
        for result in round_results:
            self.conversation_history.append({
                "agent": result["agent"],
                "content": result["response"],
                "timestamp": time.time()
            })
        
        # Update consensus status
        self.consensus_reached = self._check_consensus()
    
    def _check_consensus(self) -> bool:
        """
        Check if consensus has been reached.
        
        Returns:
            True if consensus reached, False otherwise
        """
        # Simple implementation - can be enhanced with more sophisticated consensus detection
        if len(self.conversation_history) < 2:
            return False
        
        # Check if the last two responses are similar enough
        last_two = self.conversation_history[-2:]
        if len(last_two) < 2:
            return False
        
        # Simple similarity check based on length
        len1 = len(last_two[0]["content"])
        len2 = len(last_two[1]["content"])
        similarity = min(len1, len2) / max(len1, len2)
        
        return similarity > 0.8  # 80% similarity threshold
    
    async def _generate_final_consensus(self) -> Dict[str, Any]:
        """
        Generate the final consensus summary.
        
        Returns:
            Dictionary containing consensus summary
        """
        # Get the last round's responses
        if not self.conversation_history:
            return {"status": "No discussion occurred"}
        
        # Calculate average confidence if confidence tracker exists
        avg_confidence = {}
        if hasattr(self, 'confidence_tracker') and self.confidence_tracker:
            for role, confidences in self.confidence_tracker.items():
                if confidences:  # Only calculate if there are confidence values
                    avg_confidence[role] = sum(confidences) / len(confidences)
        
        # Generate consensus summary
        consensus = {
            "status": "Consensus reached" if self._check_consensus() else "No clear consensus",
            "participants": len(self.agents),
            "rounds": len(self.conversation_history) // len(self.agents),
            "average_confidence": avg_confidence,
            "key_points": self._extract_key_points()
        }
        
        return consensus
    
    def _extract_key_points(self) -> List[str]:
        """
        Extract key points from the deliberation.
        
        Returns:
            List of key points
        """
        # Simple implementation - can be enhanced with more sophisticated extraction
        key_points = []
        
        # Use the last response from each agent
        for msg in self.conversation_history:
            agent = msg["agent"]
            role = agent.role  # Get role from agent object
            content = msg["content"]
            
            # Extract first sentence of each paragraph as key point
            paragraphs = content.split("\n\n")
            for para in paragraphs:
                if para.strip():
                    first_sentence = para.split(". ")[0]
                    key_points.append(f"{role}: {first_sentence}")
        
        return key_points
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics for the deliberation.
        
        Returns:
            Dictionary containing performance metrics
        """
        # Get performance metrics from API client
        api_metrics = self.api_client.get_performance_stats()
        
        # Calculate deliberation metrics
        deliberation_metrics = {
            "total_rounds": len(self.conversation_history) // len(self.agents),
            "consensus_reached": self.consensus_reached,
            "total_responses": len(self.conversation_history),
            "average_response_time": sum(entry.get("response_time", 0) for entry in self.conversation_history) / len(self.conversation_history) if self.conversation_history else 0
        }
        
        return {
            "api_metrics": api_metrics,
            "deliberation_metrics": deliberation_metrics
        }

    def _create_agent(
        self,
        role: str,
        system_message: str,
        memory_size: int = 10,
        max_tokens: Optional[int] = None
    ) -> EnhancedAgent:
        """
        Create an individual agent with specific configuration.
        
        Args:
            role: The role of the agent
            system_message: System message for the agent
            memory_size: Maximum number of memories to keep (not used)
            max_tokens: Maximum tokens to generate (not used)
            
        Returns:
            Configured EnhancedAgent instance
        """
        return EnhancedAgent(
            role=role,
            api_key=self.api_client.api_key,
            base_url=self.api_client.base_url,
            model=self.model,
            require_confirmation=False  # Always set to False to avoid multiple confirmations
        )

