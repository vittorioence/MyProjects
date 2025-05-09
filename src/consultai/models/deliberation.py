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
        Check if a consensus has been reached among agents.
        
        Returns:
            Boolean indicating whether consensus has been reached
        """
        # Need at least 2 responses to check consensus
        if len(self.conversation_history) < 2:
            return False
        
        # Get the latest response from each agent
        latest_responses = {}
        for entry in reversed(self.conversation_history):
            agent_key = entry["agent"].role
            if agent_key not in latest_responses:
                latest_responses[agent_key] = entry["content"]
            
            # Stop once we have a response from each agent
            if len(latest_responses) == len(self.agents):
                break
        
        # Extract key points from each response
        key_points = {}
        agreement_scores = {}
        
        for agent_key, response in latest_responses.items():
            # Extract key points (simplified implementation)
            points = self._extract_agent_key_points(response)
            key_points[agent_key] = points
            
            # Update confidence tracker
            try:
                if "confidence:" in response.lower():
                    confidence_str = response.lower().split("confidence:")[1].split("\n")[0].strip()
                    try:
                        # Try to extract numeric confidence value
                        if "/" in confidence_str:
                            confidence = float(confidence_str.split("/")[0]) / float(confidence_str.split("/")[1])
                        elif "%" in confidence_str:
                            confidence = float(confidence_str.replace("%", "")) / 100
                        else:
                            # Try to directly parse as float
                            confidence = float(confidence_str)
                            # If it's a value greater than 1, assume it's out of 10
                            if confidence > 1:
                                confidence = confidence / 10
                        self.confidence_tracker[agent_key] = min(1.0, max(0.0, confidence))  # Clamp to [0, 1]
                    except:
                        # If parsing fails, use a default medium confidence
                        self.confidence_tracker[agent_key] = 0.7
                else:
                    # No confidence found, use default
                    self.confidence_tracker[agent_key] = 0.5
            except Exception as e:
                # Fall back to default confidence on any error
                logger.warning(f"Error extracting confidence for {agent_key}: {str(e)}")
                self.confidence_tracker[agent_key] = 0.5
        
        # Calculate agreement between agents
        if len(key_points) < 2:
            return False
        
        # Check for agreement on main recommendations
        agent_keys = list(key_points.keys())
        for i in range(len(agent_keys)):
            for j in range(i+1, len(agent_keys)):
                agent1 = agent_keys[i]
                agent2 = agent_keys[j]
                
                # Calculate semantic similarity between key points
                agreement_score = self._calculate_agreement_score(key_points[agent1], key_points[agent2])
                agreement_key = f"{agent1}_{agent2}"
                agreement_scores[agreement_key] = agreement_score
        
        # Calculate average agreement score
        avg_agreement = sum(agreement_scores.values()) / len(agreement_scores) if agreement_scores else 0
        
        # Check if average agreement exceeds threshold (0.8 = high agreement)
        return avg_agreement > 0.8
    
    def _extract_agent_key_points(self, response: str) -> List[str]:
        """
        Extract key points from an agent's response.
        
        Args:
            response: The agent's response text
            
        Returns:
            List of key points extracted from the response
        """
        key_points = []
        
        # Look for structured sections in the response
        sections = ["recommendation", "conclusion", "assessment", "approach", "solution"]
        
        # Try to extract key points from specific sections
        for section in sections:
            if section.lower() in response.lower():
                # Get the paragraph containing the section
                parts = response.lower().split(section.lower())
                if len(parts) > 1:
                    paragraph = parts[1].split("\n\n")[0].strip()
                    key_points.append(paragraph)
        
        # If no structured sections found, extract sentences with key terms
        if not key_points:
            key_terms = ["should", "recommend", "suggest", "propose", "advise"]
            sentences = response.split(".")
            
            for sentence in sentences:
                for term in key_terms:
                    if term.lower() in sentence.lower():
                        key_points.append(sentence.strip())
                        break
        
        return key_points
    
    def _calculate_agreement_score(self, points1: List[str], points2: List[str]) -> float:
        """
        Calculate a simple agreement score between two sets of key points.
        In a full implementation, this would use semantic similarity.
        
        Args:
            points1: First list of key points
            points2: Second list of key points
            
        Returns:
            Agreement score between 0.0 and 1.0
        """
        # Simple implementation using word overlap
        # In a complete implementation, this would use embeddings and cosine similarity
        
        if not points1 or not points2:
            return 0.0
        
        # Calculate word overlap between points
        total_comparisons = 0
        total_similarity = 0.0
        
        for p1 in points1:
            for p2 in points2:
                words1 = set(p1.lower().split())
                words2 = set(p2.lower().split())
                
                if not words1 or not words2:
                    continue
                
                # Calculate Jaccard similarity
                intersection = len(words1.intersection(words2))
                union = len(words1.union(words2))
                
                if union > 0:
                    similarity = intersection / union
                    total_similarity += similarity
                    total_comparisons += 1
        
        # Calculate average similarity
        return total_similarity / total_comparisons if total_comparisons > 0 else 0.0
    
    async def _generate_final_consensus(self) -> Dict[str, Any]:
        """
        Generate a final consensus based on agent responses.
        
        Returns:
            Dictionary containing final consensus information
        """
        if not self.conversation_history:
            return {
                "summary": "No deliberation occurred",
                "recommendation": "No recommendation available",
                "confidence": 0.0,
                "key_considerations": []
            }
        
        # Get the latest response from each agent
        latest_responses = {}
        for entry in reversed(self.conversation_history):
            agent_key = entry["agent"].role
            if agent_key not in latest_responses:
                latest_responses[agent_key] = entry["content"]
            
            # Stop once we have a response from each agent
            if len(latest_responses) == len(self.agents):
                break
        
        # Collect all key points
        all_key_points = []
        for role, response in latest_responses.items():
            points = self._extract_agent_key_points(response)
            all_key_points.extend(points)
        
        # Extract key ethical principles mentioned
        ethical_principles = self._extract_ethical_principles()
        
        # Create prompt for generating final consensus
        prompt = f"""Based on the following conversation about an ethical case study, generate a comprehensive final consensus.

CASE STUDY:
{self.case_study}

KEY POINTS FROM DISCUSSION:
{' '.join(all_key_points)}

ETHICAL PRINCIPLES MENTIONED:
{', '.join(ethical_principles)}

Generate a final consensus with the following components:
1. Summary of the ethical dilemma
2. Analysis of key ethical principles involved
3. Recommended approach with clear justification
4. Additional considerations for implementation
5. Confidence level in this recommendation (high, medium, or low)"""

        # Use API to generate final consensus
        response = await self.api_client.make_request(prompt)
        content = response.get("content", "")
        
        # Parse the response
        summary = ""
        recommendation = ""
        confidence = 0.0
        key_considerations = []
        
        # Extract summary
        if "summary" in content.lower():
            parts = content.lower().split("summary")
            if len(parts) > 1:
                summary_text = parts[1].split("\n\n")[0].strip()
                summary = summary_text
        
        # Extract recommendation
        if "recommend" in content.lower():
            parts = content.lower().split("recommend")
            if len(parts) > 1:
                recommendation_text = parts[1].split("\n\n")[0].strip()
                recommendation = recommendation_text
        
        # Extract confidence
        confidence_map = {"high": 0.9, "medium": 0.7, "low": 0.5}
        if "confidence" in content.lower():
            for level, value in confidence_map.items():
                if level in content.lower():
                    confidence = value
                    break
        
        # Extract considerations
        if "consideration" in content.lower():
            parts = content.lower().split("consideration")
            if len(parts) > 1:
                considerations_text = parts[1].split("\n\n")[0].strip()
                key_considerations = [
                    item.strip() 
                    for item in considerations_text.split("\n") 
                    if item.strip() and not item.strip().startswith(":")
                ]
        
        # If we couldn't extract structured fields, use the whole content
        if not summary and not recommendation:
            summary = "See full consensus below"
            recommendation = content
        
        # Calculate average confidence from agent confidence values
        agent_confidences = list(self.confidence_tracker.values())
        avg_agent_confidence = sum(agent_confidences) / len(agent_confidences) if agent_confidences else 0.7
        
        # Blend AI-generated confidence with agent confidences
        blended_confidence = (confidence + avg_agent_confidence) / 2
        
        return {
            "summary": summary,
            "recommendation": recommendation,
            "confidence": blended_confidence,
            "key_considerations": key_considerations,
            "ethical_principles": ethical_principles,
            "full_text": content
        }

    def _extract_ethical_principles(self) -> List[str]:
        """
        Extract ethical principles mentioned in the conversation.
        
        Returns:
            List of ethical principles mentioned
        """
        principles = set()
        principle_keywords = {
            "autonomy": ["autonomy", "self-determination", "informed consent", "patient choice"],
            "beneficence": ["beneficence", "best interest", "patient welfare", "benefit"],
            "non-maleficence": ["non-maleficence", "harm", "do no harm", "risk"],
            "justice": ["justice", "fairness", "equity", "allocation", "resources"],
            "dignity": ["dignity", "respect", "worth", "value"],
            "veracity": ["veracity", "truth", "honesty", "transparency"],
            "fidelity": ["fidelity", "commitment", "promise", "loyalty"]
        }
        
        # Search through conversation history
        for entry in self.conversation_history:
            content = entry["content"].lower()
            for principle, keywords in principle_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        principles.add(principle)
                        break
        
        return list(principles)
    
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

