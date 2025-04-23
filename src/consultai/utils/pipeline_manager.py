"""
Pipeline Manager Module for ConsultAI.
This module orchestrates the deliberation process with specific agents and model settings.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from pathlib import Path

from consultai.models.deliberation import DeliberationManager
from consultai.config.model_manager import ModelManager, ModelTier
from consultai.config.dashboard import DashboardConfig, CaseStudyType, RoleConfig
from consultai.config.config import get_agents_config, get_api_config

# Configure logging
logger = logging.getLogger(__name__)

class PipelineManager:
    """
    Manages the complete deliberation pipeline with specific model and agent configurations.
    """
    
    def __init__(
        self,
        model_tier: str = "economy",  # Accept string value
        require_confirmation: bool = True,
        max_concurrent: int = 2  # Default to 2 for parallel agent responses
    ):
        """
        Initialize the pipeline manager.
        
        Args:
            model_tier: The model tier to use (economy, balanced, performance)
            require_confirmation: Whether to require confirmation for API requests
            max_concurrent: Maximum number of concurrent API requests
        """
        try:
            # Convert string model tier to enum
            model_tier_enum = ModelTier[model_tier.upper()]
        except KeyError:
            logger.warning(f"Invalid model tier '{model_tier}', defaulting to 'economy'")
            model_tier_enum = ModelTier.ECONOMY
        
        self.model_manager = ModelManager(tier=model_tier_enum)
        self.dashboard = DashboardConfig(
            model_tier=model_tier_enum,
            max_parallel_requests=max_concurrent,
            require_confirmation=require_confirmation
        )
        self.max_concurrent = max_concurrent
        self.require_confirmation = require_confirmation
    
    async def run_autonomy_case(
        self,
        case_study_path: Optional[str] = None,
        custom_case_text: Optional[str] = None,
        roles: Optional[List[str]] = None,
        max_rounds: int = 3,
        max_concurrent: Optional[int] = None,
        require_confirmation: bool = False
    ) -> Dict[str, Any]:
        """
        Run a deliberation on an autonomy case study with specific agents.
        
        Args:
            case_study_path: Path to the case study file (optional)
            custom_case_text: Custom case study text (optional)
            roles: List of role names to use (defaults to ["attending_physician", "nurse_manager"])
            max_rounds: Maximum number of deliberation rounds
            max_concurrent: Maximum number of concurrent requests (optional)
            require_confirmation: Whether to require confirmation for API requests
            
        Returns:
            Dictionary containing deliberation results and performance metrics
        """
        # Set default roles if not provided
        if roles is None:
            roles = ["attending_physician", "nurse_manager"]
        
        # Get case study text
        case_text = self._get_case_study_text(case_study_path, custom_case_text)
        
        # Get model configuration
        model_config = self.model_manager.get_model_for_task("deliberation")
        
        # Create custom role configurations
        role_configs = {
            "attending_physician": RoleConfig(
                name="Attending Physician",
                description="Senior medical professional responsible for patient care",
                system_message="You are an experienced attending physician with expertise in medical ethics and patient care.",
                memory_size=5,
                token_limit=model_config.max_tokens,
                required_capabilities=["context_understanding", "ethical_analysis"]
            ),
            "nurse_manager": RoleConfig(
                name="Nurse Manager",
                description="Senior nursing professional managing patient care",
                system_message="You are a nurse manager with extensive experience in patient care coordination and healthcare ethics.",
                memory_size=5,
                token_limit=model_config.max_tokens,
                required_capabilities=["context_understanding", "ethical_analysis"]
            )
        }
        
        # Initialize deliberation manager with max_concurrent if provided
        manager = DeliberationManager(
            case_study=case_text,
            max_concurrent=max_concurrent or self.max_concurrent,
            require_confirmation=require_confirmation
        )
        
        # Override default agents with our specific roles
        manager.agents = []
        for role in roles:
            if role in role_configs:
                config = role_configs[role]
                manager.agents.append(manager._create_agent(
                    role=role,
                    system_message=config.system_message,
                    memory_size=config.memory_size,
                    max_tokens=config.token_limit
                ))
        
        # Run deliberation
        results = await manager.run_deliberation(max_rounds=max_rounds)
        
        # Extract and format final output
        final_output = self._format_final_output(results)
        
        return final_output
    
    def _get_case_study_text(
        self,
        case_study_path: Optional[str],
        custom_case_text: Optional[str]
    ) -> str:
        """
        Get the case study text from either a file or custom text.
        
        Args:
            case_study_path: Path to the case study file
            custom_case_text: Custom case study text
            
        Returns:
            Case study text
        """
        if custom_case_text:
            return custom_case_text
        
        if case_study_path:
            try:
                with open(case_study_path, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Error reading case study file: {e}")
                raise
        
        # If neither is provided, use the default autonomy case study
        case_config = self.dashboard.get_case_study_config(CaseStudyType.AUTONOMY)
        with open(case_config.file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _format_final_output(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the final output with deliberation results and performance metrics.
        
        Args:
            results: Raw deliberation results
            
        Returns:
            Formatted output dictionary
        """
        # Extract key metrics
        api_metrics = results.get("performance_metrics", {}).get("api_metrics", {})
        deliberation_metrics = results.get("performance_metrics", {}).get("deliberation_metrics", {})
        
        # Format the output
        output = {
            "case_summary": {
                "title": "Patient Autonomy Case Analysis",
                "start_time": results.get("start_time"),
                "end_time": results.get("end_time"),
                "total_rounds": deliberation_metrics.get("total_rounds", 0),
                "consensus_reached": deliberation_metrics.get("consensus_reached", False)
            },
            "agent_responses": [],
            "final_consensus": results.get("final_consensus", {}),
            "performance_scores": {
                "response_times": {
                    "average_ms": api_metrics.get("average_response_time_ms", 0),
                    "total_ms": api_metrics.get("total_response_time_ms", 0)
                },
                "token_usage": {
                    "total_tokens": api_metrics.get("total_tokens", 0),
                    "total_cost": api_metrics.get("total_cost_usd", 0)
                },
                "quality_metrics": {
                    "consensus_quality": deliberation_metrics.get("consensus_quality", 0),
                    "response_coherence": deliberation_metrics.get("response_coherence", 0)
                }
            }
        }
        
        # Add agent responses
        for round_data in results.get("rounds", []):
            for response in round_data:
                output["agent_responses"].append({
                    "role": response["agent"].role,
                    "response": response["response"],
                    "confidence": response.get("performance", {}).get("confidence", 0)
                })
        
        return output 