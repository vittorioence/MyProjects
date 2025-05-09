"""
Role Definitions Module for ConsultAI.
This module provides definitions for various agent roles used in deliberations.
"""

from typing import Dict, Any, List, Optional
import os
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

class RoleDefinition:
    """
    Defines a role for an agent in a deliberation.
    """
    
    def __init__(
        self,
        role_id: str,
        name: str,
        description: str,
        system_message: str,
        expertise_areas: List[str],
        stakeholder_perspective: Optional[str] = None,
        memory_size: int = 10,
        token_limit: int = 4000,
        required_capabilities: Optional[List[str]] = None
    ):
        """
        Initialize a role definition.
        
        Args:
            role_id: Unique identifier for the role
            name: Display name for the role
            description: Brief description of the role
            system_message: System message for the agent
            expertise_areas: List of expertise areas
            stakeholder_perspective: Which stakeholder this role represents
            memory_size: Number of messages to remember
            token_limit: Maximum tokens for responses
            required_capabilities: Required model capabilities
        """
        self.role_id = role_id
        self.name = name
        self.description = description
        self.system_message = system_message
        self.expertise_areas = expertise_areas
        self.stakeholder_perspective = stakeholder_perspective
        self.memory_size = memory_size
        self.token_limit = token_limit
        self.required_capabilities = required_capabilities or ["context_understanding", "ethical_analysis"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary representation.
        
        Returns:
            Dictionary representation of the role
        """
        return {
            "role_id": self.role_id,
            "name": self.name,
            "description": self.description,
            "system_message": self.system_message,
            "expertise_areas": self.expertise_areas,
            "stakeholder_perspective": self.stakeholder_perspective,
            "memory_size": self.memory_size,
            "token_limit": self.token_limit,
            "required_capabilities": self.required_capabilities
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RoleDefinition':
        """
        Create a role definition from a dictionary.
        
        Args:
            data: Dictionary representation of the role
            
        Returns:
            RoleDefinition instance
        """
        return cls(
            role_id=data["role_id"],
            name=data["name"],
            description=data["description"],
            system_message=data["system_message"],
            expertise_areas=data["expertise_areas"],
            stakeholder_perspective=data.get("stakeholder_perspective"),
            memory_size=data.get("memory_size", 10),
            token_limit=data.get("token_limit", 4000),
            required_capabilities=data.get("required_capabilities", ["context_understanding", "ethical_analysis"])
        )


class RoleManager:
    """
    Manages role definitions for deliberations.
    """
    
    def __init__(self, roles_path: Optional[str] = None):
        """
        Initialize the role manager.
        
        Args:
            roles_path: Path to role definitions file
        """
        self.roles_path = roles_path or os.path.join("data", "roles", "role_definitions.json")
        self.roles: Dict[str, RoleDefinition] = {}
        self._load_default_roles()
        
        # Load custom roles if available
        if os.path.exists(self.roles_path):
            self._load_roles_from_file()
    
    def _load_default_roles(self):
        """Load the default set of roles."""
        # Healthcare provider roles
        self.roles["attending_physician"] = RoleDefinition(
            role_id="attending_physician",
            name="Attending Physician",
            description="Senior medical professional responsible for patient care decisions",
            system_message=(
                "You are an experienced attending physician with expertise in medical ethics and patient care. "
                "Your role is to provide medical insights and consider the clinical implications of various "
                "approaches. Prioritize medical best practices, patient outcomes, and evidence-based medicine. "
                "Consider both immediate clinical needs and long-term prognosis when analyzing cases."
            ),
            expertise_areas=["clinical medicine", "medical ethics", "patient care", "treatment planning"],
            stakeholder_perspective="healthcare provider"
        )
        
        self.roles["nurse_manager"] = RoleDefinition(
            role_id="nurse_manager",
            name="Nurse Manager",
            description="Senior nursing professional managing patient care and staff",
            system_message=(
                "You are a nurse manager with extensive experience in patient care coordination and healthcare ethics. "
                "Your role is to provide the nursing perspective, focusing on patient care, family communication, "
                "and day-to-day implementation. Consider care practicalities, resource requirements, and staff workload. "
                "You have direct patient contact and can speak to the patient's reported experience."
            ),
            expertise_areas=["nursing care", "patient advocacy", "care coordination", "family communication"],
            stakeholder_perspective="healthcare provider"
        )
        
        # Ethics roles
        self.roles["clinical_ethicist"] = RoleDefinition(
            role_id="clinical_ethicist",
            name="Clinical Ethicist",
            description="Professional specializing in healthcare ethics and ethical deliberation",
            system_message=(
                "You are a clinical ethicist with deep expertise in bioethics principles and healthcare decision-making. "
                "Your role is to identify and analyze the ethical dimensions of each case. Focus on the ethical principles "
                "of autonomy, beneficence, non-maleficence, and justice. Help clarify value conflicts and propose "
                "ethically sound approaches to resolution."
            ),
            expertise_areas=["bioethics", "ethical deliberation", "ethical frameworks", "values clarification"],
            stakeholder_perspective="ethics specialist"
        )
        
        # Patient advocate roles
        self.roles["patient_advocate"] = RoleDefinition(
            role_id="patient_advocate",
            name="Patient Advocate",
            description="Represents the patient's interests and perspective",
            system_message=(
                "You are a patient advocate who champions the patient's rights, preferences, and interests. "
                "Your role is to ensure the patient's voice is heard and their autonomy respected. Focus on "
                "patient values, quality of life considerations, and the impact of various approaches on the "
                "patient's dignity and self-determination. Question proposals that marginalize patient preferences."
            ),
            expertise_areas=["patient rights", "autonomy", "healthcare navigation", "quality of life"],
            stakeholder_perspective="patient"
        )
        
        # Administrative roles
        self.roles["hospital_administrator"] = RoleDefinition(
            role_id="hospital_administrator",
            name="Hospital Administrator",
            description="Healthcare facility administrator responsible for operations and resources",
            system_message=(
                "You are a hospital administrator with responsibility for resource allocation, policy implementation, "
                "and institutional liability. Your role is to consider the organizational and resource implications "
                "of various approaches. Focus on resource constraints, precedent-setting, policy compliance, and "
                "sustainable practices. You must balance individual patient needs with system-level considerations."
            ),
            expertise_areas=["healthcare management", "resource allocation", "policy compliance", "risk management"],
            stakeholder_perspective="healthcare system"
        )
        
        # Legal roles
        self.roles["healthcare_attorney"] = RoleDefinition(
            role_id="healthcare_attorney",
            name="Healthcare Attorney",
            description="Legal expert specializing in healthcare law and regulations",
            system_message=(
                "You are a healthcare attorney with expertise in medical law, patient rights, and healthcare regulations. "
                "Your role is to identify legal considerations and ensure compliance with relevant laws. Focus on legal "
                "precedents, patient rights legislation, and institutional liability. Provide guidance on legally sound "
                "approaches that protect all parties while respecting ethical principles."
            ),
            expertise_areas=["healthcare law", "patient rights", "regulatory compliance", "risk management"],
            stakeholder_perspective="legal advisor"
        )
        
        # Family roles
        self.roles["family_representative"] = RoleDefinition(
            role_id="family_representative",
            name="Family Representative",
            description="Represents the family's interests and perspective",
            system_message=(
                "You are a representative of the patient's family, with deep concerns for their loved one's wellbeing. "
                "Your role is to voice family perspectives, concerns, and questions. You care deeply about the patient "
                "but may have your own views on what constitutes the best care. Consider family dynamics, cultural "
                "factors, and the impact of decisions on family members."
            ),
            expertise_areas=["family dynamics", "caregiver perspective", "emotional support", "cultural considerations"],
            stakeholder_perspective="family"
        )
        
        # Chaplain/spiritual advisor
        self.roles["chaplain"] = RoleDefinition(
            role_id="chaplain",
            name="Chaplain",
            description="Spiritual advisor providing support and perspective",
            system_message=(
                "You are a hospital chaplain with experience supporting patients and families through difficult healthcare decisions. "
                "Your role is to consider spiritual and existential dimensions of cases. Focus on meaning, values, and how "
                "decisions align with deeper beliefs. You provide non-judgmental spiritual support while respecting diverse "
                "religious and cultural perspectives."
            ),
            expertise_areas=["spiritual care", "existential support", "cultural competence", "values exploration"],
            stakeholder_perspective="spiritual advisor"
        )
        
        # Social worker
        self.roles["social_worker"] = RoleDefinition(
            role_id="social_worker",
            name="Social Worker",
            description="Healthcare social worker focusing on patient support systems",
            system_message=(
                "You are a healthcare social worker with expertise in psychosocial factors and support systems. "
                "Your role is to consider social determinants of health, family systems, and practical support needs. "
                "Focus on discharge planning, community resources, and continuity of care. Help identify barriers to "
                "implementing various approaches and suggest practical solutions."
            ),
            expertise_areas=["psychosocial assessment", "resource navigation", "family systems", "care transitions"],
            stakeholder_perspective="support services"
        )
    
    def _load_roles_from_file(self):
        """Load role definitions from file."""
        try:
            with open(self.roles_path, 'r', encoding='utf-8') as f:
                roles_data = json.load(f)
                
                for role_data in roles_data:
                    role = RoleDefinition.from_dict(role_data)
                    self.roles[role.role_id] = role
                    
            logger.info(f"Loaded {len(roles_data)} role definitions from {self.roles_path}")
        except Exception as e:
            logger.error(f"Error loading role definitions from {self.roles_path}: {e}")
    
    def save_roles_to_file(self, path: Optional[str] = None):
        """
        Save role definitions to file.
        
        Args:
            path: Path to save role definitions (optional)
        """
        save_path = path or self.roles_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            roles_data = [role.to_dict() for role in self.roles.values()]
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(roles_data, f, indent=2)
                
            logger.info(f"Saved {len(roles_data)} role definitions to {save_path}")
        except Exception as e:
            logger.error(f"Error saving role definitions to {save_path}: {e}")
    
    def get_role(self, role_id: str) -> Optional[RoleDefinition]:
        """
        Get a role definition by ID.
        
        Args:
            role_id: Role ID to look up
            
        Returns:
            RoleDefinition if found, None otherwise
        """
        return self.roles.get(role_id)
    
    def get_all_roles(self) -> List[RoleDefinition]:
        """
        Get all role definitions.
        
        Returns:
            List of all role definitions
        """
        return list(self.roles.values())
    
    def get_case_type_roles(self, case_type: str) -> List[RoleDefinition]:
        """
        Get roles recommended for a specific case type.
        
        Args:
            case_type: Type of case study
            
        Returns:
            List of recommended role definitions
        """
        if case_type == "autonomy":
            return [
                self.roles["attending_physician"],
                self.roles["patient_advocate"],
                self.roles["clinical_ethicist"],
                self.roles["family_representative"]
            ]
        elif case_type == "beneficence":
            return [
                self.roles["attending_physician"],
                self.roles["nurse_manager"],
                self.roles["clinical_ethicist"],
                self.roles["patient_advocate"]
            ]
        elif case_type == "justice":
            return [
                self.roles["hospital_administrator"],
                self.roles["clinical_ethicist"],
                self.roles["attending_physician"],
                self.roles["social_worker"]
            ]
        elif case_type == "resource_allocation":
            return [
                self.roles["hospital_administrator"],
                self.roles["attending_physician"],
                self.roles["clinical_ethicist"],
                self.roles["nurse_manager"]
            ]
        else:
            # Default to a standard set of roles
            return [
                self.roles["attending_physician"],
                self.roles["nurse_manager"],
                self.roles["clinical_ethicist"],
                self.roles["patient_advocate"]
            ]
    
    def add_role(self, role: RoleDefinition) -> None:
        """
        Add a new role definition.
        
        Args:
            role: Role definition to add
        """
        self.roles[role.role_id] = role
    
    def remove_role(self, role_id: str) -> bool:
        """
        Remove a role definition.
        
        Args:
            role_id: Role ID to remove
            
        Returns:
            True if role was removed, False if not found
        """
        if role_id in self.roles:
            del self.roles[role_id]
            return True
        return False


# Create a singleton instance
ROLE_MANAGER = RoleManager()

def get_role_manager() -> RoleManager:
    """
    Get the singleton role manager instance.
    
    Returns:
        RoleManager instance
    """
    return ROLE_MANAGER 