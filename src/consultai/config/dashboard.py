"""
Dashboard Configuration Module for ConsultAI.
This module provides a centralized dashboard for managing case studies, roles, and other key settings.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from consultai.config.model_manager import ModelTier

class CaseStudyType(Enum):
    """Types of case studies"""
    AUTONOMY = "autonomy"
    BENEFICENCE = "beneficence"
    JUSTICE = "justice"
    RESOURCE_ALLOCATION = "resource_allocation"
    GENERAL = "general"

@dataclass
class RoleConfig:
    """Configuration for a specific role"""
    name: str
    description: str
    system_message: str
    memory_size: int
    token_limit: int
    required_capabilities: List[str]

@dataclass
class CaseStudyConfig:
    """Configuration for a case study"""
    type: CaseStudyType
    title: str
    description: str
    file_path: Path
    required_roles: List[str]
    ethical_principles: List[str]
    complexity_level: int  # 1-5

class DashboardConfig:
    """
    Dashboard configuration for ConsultAI.
    Centralizes management of case studies, roles, and system settings.
    """
    
    # Role definitions
    ROLES = {
        "ethicist": RoleConfig(
            name="Ethicist",
            description="Expert in ethical theory and moral philosophy",
            system_message="You are an expert in ethical theory and moral philosophy.",
            memory_size=5,
            token_limit=2000,
            required_capabilities=["complex_reasoning", "ethical_analysis"]
        ),
        "healthcare_professional": RoleConfig(
            name="Healthcare Professional",
            description="Experienced clinical practitioner",
            system_message="You are a healthcare professional with extensive clinical experience.",
            memory_size=5,
            token_limit=2000,
            required_capabilities=["context_understanding", "ethical_analysis"]
        ),
        "patient_advocate": RoleConfig(
            name="Patient Advocate",
            description="Representative of patient interests",
            system_message="You represent patient interests and healthcare consumer rights.",
            memory_size=5,
            token_limit=2000,
            required_capabilities=["context_understanding", "creativity"]
        ),
        "policy_expert": RoleConfig(
            name="Policy Expert",
            description="Healthcare policy and regulation specialist",
            system_message="You are an expert in healthcare policy and regulations.",
            memory_size=5,
            token_limit=2000,
            required_capabilities=["complex_reasoning", "context_understanding"]
        ),
        "technologist": RoleConfig(
            name="Technologist",
            description="Healthcare technology specialist",
            system_message="You are an expert in healthcare technology and innovation.",
            memory_size=5,
            token_limit=2000,
            required_capabilities=["creativity", "context_understanding"]
        )
    }
    
    # Case study definitions
    CASE_STUDIES = {
        CaseStudyType.AUTONOMY: CaseStudyConfig(
            type=CaseStudyType.AUTONOMY,
            title="Patient Autonomy in End-of-Life Care",
            description="Case study focusing on patient autonomy and decision-making",
            file_path=Path("data/case_studies/autonomy/autonomy_case_1.txt"),
            required_roles=["ethicist", "healthcare_professional", "patient_advocate"],
            ethical_principles=["autonomy", "beneficence", "non-maleficence"],
            complexity_level=3
        ),
        CaseStudyType.BENEFICENCE: CaseStudyConfig(
            type=CaseStudyType.BENEFICENCE,
            title="Beneficence in Resource Allocation",
            description="Case study focusing on beneficence and non-maleficence",
            file_path=Path("data/case_studies/beneficence/beneficence_case.txt"),
            required_roles=["ethicist", "healthcare_professional", "policy_expert"],
            ethical_principles=["beneficence", "non-maleficence", "justice"],
            complexity_level=4
        ),
        CaseStudyType.JUSTICE: CaseStudyConfig(
            type=CaseStudyType.JUSTICE,
            title="Justice in Healthcare Access",
            description="Case study focusing on justice in healthcare",
            file_path=Path("data/case_studies/justice/justice_case.txt"),
            required_roles=["ethicist", "policy_expert", "patient_advocate"],
            ethical_principles=["justice", "autonomy", "beneficence"],
            complexity_level=5
        ),
        CaseStudyType.RESOURCE_ALLOCATION: CaseStudyConfig(
            type=CaseStudyType.RESOURCE_ALLOCATION,
            title="Resource Allocation in Crisis",
            description="Case study focusing on resource allocation and distributive justice",
            file_path=Path("data/case_studies/resource_allocation/resource_allocation_case.txt"),
            required_roles=["ethicist", "healthcare_professional", "policy_expert", "technologist"],
            ethical_principles=["justice", "beneficence", "utility"],
            complexity_level=5
        ),
        CaseStudyType.GENERAL: CaseStudyConfig(
            type=CaseStudyType.GENERAL,
            title="General Ethics Committee Case",
            description="General case study for ethics committee deliberation",
            file_path=Path("data/case_studies/general/case_study_1.txt"),
            required_roles=["ethicist", "healthcare_professional", "patient_advocate", "policy_expert"],
            ethical_principles=["autonomy", "beneficence", "non-maleficence", "justice"],
            complexity_level=3
        )
    }
    
    def __init__(
        self,
        model_tier: ModelTier = ModelTier.BALANCED,
        max_parallel_requests: int = 3,
        require_confirmation: bool = True
    ):
        """
        Initialize the dashboard configuration.
        
        Args:
            model_tier: The model tier to use
            max_parallel_requests: Maximum number of parallel API requests
            require_confirmation: Whether to require confirmation for API requests
        """
        self.model_tier = model_tier
        self.max_parallel_requests = max_parallel_requests
        self.require_confirmation = require_confirmation
    
    def get_role_config(self, role_name: str) -> RoleConfig:
        """
        Get configuration for a specific role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            RoleConfig for the specified role
        """
        return self.ROLES[role_name]
    
    def get_case_study_config(self, case_type: CaseStudyType) -> CaseStudyConfig:
        """
        Get configuration for a specific case study.
        
        Args:
            case_type: Type of case study
            
        Returns:
            CaseStudyConfig for the specified case study
        """
        return self.CASE_STUDIES[case_type]
    
    def get_available_roles(self) -> Dict[str, RoleConfig]:
        """
        Get all available role configurations.
        
        Returns:
            Dictionary of all available roles
        """
        return self.ROLES.copy()
    
    def get_available_case_studies(self) -> Dict[CaseStudyType, CaseStudyConfig]:
        """
        Get all available case study configurations.
        
        Returns:
            Dictionary of all available case studies
        """
        return self.CASE_STUDIES.copy()
    
    def get_roles_for_case_study(self, case_type: CaseStudyType) -> List[RoleConfig]:
        """
        Get all roles required for a specific case study.
        
        Args:
            case_type: Type of case study
            
        Returns:
            List of RoleConfig objects for the required roles
        """
        case_study = self.CASE_STUDIES[case_type]
        return [self.ROLES[role] for role in case_study.required_roles]
    
    def get_system_settings(self) -> Dict[str, Any]:
        """
        Get current system settings.
        
        Returns:
            Dictionary of current system settings
        """
        return {
            "model_tier": self.model_tier,
            "max_parallel_requests": self.max_parallel_requests,
            "require_confirmation": self.require_confirmation
        } 