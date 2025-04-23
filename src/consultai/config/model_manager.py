"""
Model Management Module for ConsultAI.
This module provides centralized management of language models used throughout the system.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ModelTier(Enum):
    """Model tier options for cost-performance tradeoff"""
    ECONOMY = "economy"      # Optimized for cost
    BALANCED = "balanced"    # Balance between cost and performance
    PERFORMANCE = "performance"  # Optimized for performance

class TaskTier(Enum):
    """Task tier options for different complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    PERFORMANCE = "performance"

class TaskType(Enum):
    """Types of tasks that can be performed"""
    DELIBERATION = "deliberation"
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    SUMMARIZATION = "summarization"

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    max_tokens: int
    temperature: float
    input_token_cost: float  # Cost per 1k tokens
    output_token_cost: float  # Cost per 1k tokens
    capabilities: list[str]

class ModelManager:
    """
    Centralized model management for ConsultAI.
    Determines which models to use for different tasks based on requirements and cost constraints.
    """
    
    # Model definitions
    MODELS = {
        "gpt-4-turbo-2024-04-09": ModelConfig(
            name="gpt-4-turbo-2024-04-09",
            max_tokens=4096,
            temperature=0.7,
            input_token_cost=0.01,
            output_token_cost=0.03,
            capabilities=[
                "Complex ethical reasoning",
                "Detailed analysis",
                "Multi-perspective evaluation",
                "Nuanced deliberation"
            ]
        ),
        "gpt-4.1-2025-04-14": ModelConfig(
            name="gpt-4.1-2025-04-14",
            max_tokens=4096,
            temperature=0.7,
            input_token_cost=0.003,
            output_token_cost=0.012,
            capabilities=[
                "Complex ethical reasoning",
                "Detailed analysis",
                "Multi-perspective evaluation",
                "Nuanced deliberation"
            ]
        ),
        "gpt-3.5-turbo": ModelConfig(
            name="gpt-3.5-turbo",
            max_tokens=4096,
            temperature=0.7,
            input_token_cost=0.0005,
            output_token_cost=0.0015,
            capabilities=[
                "Basic analysis",
                "Simple reasoning",
                "Standard summarization"
            ]
        ),
        "text-embedding-3-small": ModelConfig(
            name="text-embedding-3-small",
            max_tokens=8191,
            temperature=0.0,
            input_token_cost=0.00002,
            output_token_cost=0.00002,
            capabilities=[
                "Text embeddings",
                "Semantic search",
                "Document similarity"
            ]
        )
    }
    
    # Task-specific model recommendations
    TASK_MODELS = {
        TaskType.DELIBERATION: {
            ModelTier.ECONOMY: "gpt-4.1-2025-04-14",
            ModelTier.BALANCED: "gpt-4.1-2025-04-14",
            ModelTier.PERFORMANCE: "gpt-4.1-2025-04-14"
        },
        TaskType.ANALYSIS: {
            ModelTier.ECONOMY: "gpt-4.1-2025-04-14",
            ModelTier.BALANCED: "gpt-4.1-2025-04-14",
            ModelTier.PERFORMANCE: "gpt-4.1-2025-04-14"
        },
        TaskType.EVALUATION: {
            ModelTier.ECONOMY: "gpt-4.1-2025-04-14",
            ModelTier.BALANCED: "gpt-4.1-2025-04-14",
            ModelTier.PERFORMANCE: "gpt-4.1-2025-04-14"
        },
        TaskType.SUMMARIZATION: {
            ModelTier.ECONOMY: "gpt-4.1-2025-04-14",
            ModelTier.BALANCED: "gpt-4.1-2025-04-14",
            ModelTier.PERFORMANCE: "gpt-4.1-2025-04-14"
        }
    }
    
    def __init__(self, tier: ModelTier = ModelTier.ECONOMY):
        """
        Initialize the model manager.
        
        Args:
            tier: The model tier to use (economy, balanced, or performance)
        """
        self.tier = tier
    
    def get_model_for_task(self, task: str) -> ModelConfig:
        """
        Get the recommended model configuration for a specific task.
        
        Args:
            task: The task to get a model for (as string or TaskType enum)
            
        Returns:
            ModelConfig for the recommended model
        """
        # Convert string task to enum if needed
        if isinstance(task, str):
            try:
                task = TaskType[task.upper()]
            except KeyError:
                logger.warning(f"Invalid task type '{task}', defaulting to DELIBERATION")
                task = TaskType.DELIBERATION

        # Get model name for task and tier
        model_name = self.TASK_MODELS[task][self.tier]
        return self.MODELS[model_name]
    
    def estimate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """
        Estimate the cost for a specific model and token usage.
        
        Args:
            model_name: Name of the model
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        model = self.MODELS[model_name]
        input_cost = (input_tokens / 1000) * model.input_token_cost
        output_cost = (output_tokens / 1000) * model.output_token_cost
        return input_cost + output_cost
    
    def get_model_capabilities(self, model_name: str) -> list[str]:
        """
        Get the capabilities of a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            List of model capabilities
        """
        return self.MODELS[model_name].capabilities
    
    def get_available_models(self) -> Dict[str, ModelConfig]:
        """
        Get all available model configurations.
        
        Returns:
            Dictionary of all available models
        """
        return self.MODELS.copy()
    
    def get_task_models(self) -> Dict[str, Dict[TaskTier, str]]:
        """
        Get all task-specific model recommendations.
        
        Returns:
            Dictionary of task-specific model recommendations
        """
        return self.TASK_MODELS.copy()

def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """
    Get the configuration for a specific model.
    
    Args:
        model_name: Name of the model
        
    Returns:
        ModelConfig if found, None otherwise
    """
    return ModelManager.MODELS.get(model_name)

def get_task_model(task_type: TaskType, tier: TaskTier) -> str:
    """
    Get the appropriate model name for a given task type and tier.
    
    Args:
        task_type: Type of the task
        tier: Tier of service
        
    Returns:
        Model name as string
    """
    return ModelManager.TASK_MODELS[task_type][tier] 