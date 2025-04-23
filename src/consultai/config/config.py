"""
Centralized configuration module for ConsultAI.
This is the single source of truth for all configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CASE_STUDIES_DIR = DATA_DIR / "case_studies"

# API Configuration
API_CONFIG = {
    "api_key": os.getenv("OPENAI_API_KEY"),
    "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "model_name": "gpt-4.1-2025-04-14",
    "temperature": 0.7,
    "max_tokens": 4000,
    "embedding_model": "text-embedding-3-small",
    "parallel_requests": True,
    "delay_between_requests": 1.0,
    "timeout_seconds": 30,
    "max_retries": 3,
    "retry_delay": 1.0,
    "query_rounds": 3
}

# Token usage costs (per 1K tokens)
TOKEN_CONFIG = {
    "gpt-4-turbo-preview": {
        "input_token_cost": 0.01,
        "output_token_cost": 0.03
    },
    "gpt-4-turbo-2024-04-09": {
        "input_token_cost": 0.01,
        "output_token_cost": 0.03
    },
    "gpt-4.1-2025-04-14": {
        "input_token_cost": 0.003,
        "output_token_cost": 0.012
    },
    "gpt-3.5-turbo": {
        "input_token_cost": 0.0015,
        "output_token_cost": 0.002
    },
    "text-embedding-3-small": {
        "input_token_cost": 0.00002
    }
}

# Performance metrics thresholds
METRICS_CONFIG = {
    "response_time_threshold": 5.0,  # seconds
    "token_usage_threshold": 2000,
    "cost_threshold": 0.10,  # USD
    "error_rate_threshold": 0.05
}

# Visualization settings
VISUALIZATION_CONFIG = {
    "figure_size": (12, 8),
    "style": "seaborn",
    "color_palette": "viridis",
    "dpi": 100
}

# RAG Configuration
RAG_CONFIG = {
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "max_documents": 5,
    "similarity_threshold": 0.7
}

# Deliberation Configuration
DELIBERATION_CONFIG = {
    "roles": {
        "ethicist": {
            "system_message": "You are an expert in ethical theory and moral philosophy.",
            "memory_size": 5,
            "token_limit": 2000
        },
        "healthcare_professional": {
            "system_message": "You are a healthcare professional with extensive clinical experience.",
            "memory_size": 5,
            "token_limit": 2000
        },
        "patient_advocate": {
            "system_message": "You represent patient interests and healthcare consumer rights.",
            "memory_size": 5,
            "token_limit": 2000
        },
        "policy_expert": {
            "system_message": "You are an expert in healthcare policy and regulations.",
            "memory_size": 5,
            "token_limit": 2000
        },
        "technologist": {
            "system_message": "You are an expert in healthcare technology and innovation.",
            "memory_size": 5,
            "token_limit": 2000
        }
    },
    "consensus_threshold": 0.7,
    "max_rounds": 3,
    "min_agreement": 0.6
}

# Agent Configuration
AGENTS_CONFIG = {
    "active_roles": ["ethicist", "healthcare_professional", "patient_advocate"],
    "parallel_processing": True,
    "require_confirmation": True,
    "max_concurrent_requests": 3
}

# Evaluation Configuration
EVALUATION_CONFIG = {
    "metrics": [
        "response_time",
        "token_usage",
        "cost",
        "consensus_level",
        "innovation_score"
    ],
    "thresholds": {
        "response_time": 5.0,
        "token_usage": 2000,
        "cost": 0.10,
        "consensus_level": 0.7,
        "innovation_score": 0.6
    }
}

# Innovation Tracking
INNOVATION_CONFIG = {
    "metrics": {
        "novelty_threshold": 0.7,
        "impact_threshold": 0.6,
        "feasibility_threshold": 0.5
    },
    "tracking": {
        "save_innovations": True,
        "innovation_dir": DATA_DIR / "innovations",
        "max_stored": 100
    }
}

# Case Studies
CASE_STUDIES = {
    "justice_in_healthcare": {
        "title": "Justice in Healthcare Resource Allocation",
        "description": "Analyzing fair distribution of limited healthcare resources",
        "principles": ["justice", "fairness", "equity"],
        "file_path": CASE_STUDIES_DIR / "justice_in_healthcare.txt"
    },
    "resource_allocation": {
        "title": "Resource Allocation in Crisis",
        "description": "Ethical decision-making during healthcare crises",
        "principles": ["utility", "justice", "autonomy"],
        "file_path": CASE_STUDIES_DIR / "resource_allocation.txt"
    }
}

def get_api_config():
    """Get API configuration settings."""
    return API_CONFIG

def get_token_config():
    """Get token usage configuration."""
    return TOKEN_CONFIG

def get_metrics_config():
    """Get performance metrics configuration."""
    return METRICS_CONFIG

def get_visualization_config():
    """Get visualization settings."""
    return VISUALIZATION_CONFIG

def get_rag_config():
    """Get RAG configuration settings."""
    return RAG_CONFIG

def get_deliberation_config():
    """Get deliberation configuration settings."""
    return DELIBERATION_CONFIG

def get_agents_config():
    """Get agent configuration settings."""
    return AGENTS_CONFIG

def get_evaluation_config():
    """Get evaluation configuration settings."""
    return EVALUATION_CONFIG

def get_innovation_config():
    """Get innovation tracking configuration."""
    return INNOVATION_CONFIG

def get_case_studies():
    """Get available case studies."""
    return CASE_STUDIES 