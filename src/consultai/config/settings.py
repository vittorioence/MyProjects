"""
Simplified access to configuration settings.
This module provides a simplified interface to the main configuration.
"""

from consultai.config.config import (
    API_CONFIG,
    RAG_CONFIG,
    DELIBERATION_CONFIG,
    AGENTS_CONFIG,
    EVALUATION_CONFIG,
    CASE_STUDIES,
    PROJECT_ROOT,
    DATA_DIR,
    CASE_STUDIES_DIR
)

# Re-export all configuration
__all__ = [
    'API_CONFIG',
    'RAG_CONFIG',
    'DELIBERATION_CONFIG',
    'AGENTS_CONFIG',
    'EVALUATION_CONFIG',
    'CASE_STUDIES',
    'PROJECT_ROOT',
    'DATA_DIR',
    'CASE_STUDIES_DIR'
]

# This file now serves as a simplified interface to the main configuration
# All API and other configuration is imported from config.py

# Deliberation Configuration
DELIBERATION_CONFIG = {
    "num_turns_per_agent": 2,
    "max_history_messages": 10,
    "delay_between_turns": 1  # seconds
}

# Case Studies Configuration
CASE_STUDIES = {
    "autonomy": {
        "file_path": str(CASE_STUDIES_DIR / "autonomy" / "autonomy_case_1.txt"),
        "description": "Case study focusing on patient autonomy and decision-making"
    },
    "beneficence": {
        "file_path": str(CASE_STUDIES_DIR / "beneficence" / "beneficence_case.txt"),
        "description": "Case study focusing on beneficence and non-maleficence"
    },
    "justice": {
        "file_path": str(CASE_STUDIES_DIR / "justice" / "justice_case.txt"),
        "description": "Case study focusing on justice in healthcare"
    },
    "resource_allocation": {
        "file_path": str(CASE_STUDIES_DIR / "resource_allocation" / "resource_allocation_case.txt"),
        "description": "Case study focusing on resource allocation and distributive justice"
    },
    "general": {
        "file_path": str(CASE_STUDIES_DIR / "general" / "case_study_1.txt"),
        "description": "General case study for ethics committee deliberation"
    }
} 