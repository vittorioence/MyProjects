"""
Evaluation module for ConsultAI.
This module provides tools for evaluating the quality of ethical deliberations.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class DeliberationEvaluator:
    """
    Evaluates the quality of ethical deliberations.
    """
    
    def __init__(
        self,
        evaluation_criteria: Optional[Dict[str, float]] = None,
        output_dir: str = "output/evaluations"
    ):
        """
        Initialize the deliberation evaluator.
        
        Args:
            evaluation_criteria: Dictionary of evaluation criteria and their weights
            output_dir: Directory to save evaluation results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set default evaluation criteria if not provided
        if evaluation_criteria is None:
            self.evaluation_criteria = {
                "ethical_principle_coverage": 0.25,  # Coverage of key ethical principles
                "reasoning_quality": 0.25,           # Quality of ethical reasoning
                "evidence_usage": 0.15,              # Use of evidence from case
                "stakeholder_consideration": 0.15,   # Consideration of all stakeholders
                "practical_applicability": 0.20      # Practical applicability of recommendations
            }
        else:
            self.evaluation_criteria = evaluation_criteria
    
    def evaluate_deliberation(
        self,
        deliberation_results: Dict[str, Any],
        case_study: str,
        benchmark_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a deliberation based on ethical reasoning quality.
        
        Args:
            deliberation_results: Dictionary containing deliberation results
            case_study: Case study text
            benchmark_data: Optional benchmark data for comparison
            
        Returns:
            Dictionary of evaluation scores
        """
        # Extract data for evaluation
        final_consensus = deliberation_results.get("final_consensus", {})
        agent_responses = deliberation_results.get("agent_responses", [])
        
        # Evaluate ethical principle coverage
        principle_coverage = self._evaluate_principle_coverage(final_consensus)
        
        # Evaluate reasoning quality
        reasoning_quality = self._evaluate_reasoning_quality(final_consensus, agent_responses)
        
        # Evaluate evidence usage
        evidence_usage = self._evaluate_evidence_usage(final_consensus, case_study)
        
        # Evaluate stakeholder consideration
        stakeholder_consideration = self._evaluate_stakeholder_consideration(final_consensus, case_study)
        
        # Evaluate practical applicability
        practical_applicability = self._evaluate_practical_applicability(final_consensus)
        
        # Calculate overall score
        overall_score = (
            principle_coverage * self.evaluation_criteria["ethical_principle_coverage"] +
            reasoning_quality * self.evaluation_criteria["reasoning_quality"] +
            evidence_usage * self.evaluation_criteria["evidence_usage"] +
            stakeholder_consideration * self.evaluation_criteria["stakeholder_consideration"] +
            practical_applicability * self.evaluation_criteria["practical_applicability"]
        )
        
        # Prepare evaluation results
        evaluation_results = {
            "overall_score": overall_score,
            "component_scores": {
                "ethical_principle_coverage": principle_coverage,
                "reasoning_quality": reasoning_quality,
                "evidence_usage": evidence_usage,
                "stakeholder_consideration": stakeholder_consideration,
                "practical_applicability": practical_applicability
            },
            "strengths": self._identify_strengths(agent_responses, final_consensus),
            "areas_for_improvement": self._identify_areas_for_improvement(agent_responses, final_consensus),
            "innovation_metrics": self._calculate_innovation_metrics(agent_responses, final_consensus),
            "evaluation_timestamp": datetime.now().isoformat()
        }
        
        # Compare to benchmark if provided
        if benchmark_data:
            evaluation_results["benchmark_comparison"] = self._compare_to_benchmark(
                evaluation_results,
                benchmark_data
            )
        
        # Save evaluation results
        self._save_evaluation_results(evaluation_results)
        
        return evaluation_results
    
    def _evaluate_principle_coverage(self, final_consensus: Dict[str, Any]) -> float:
        """
        Evaluate the coverage of ethical principles.
        
        Args:
            final_consensus: Final consensus dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        # Key ethical principles that should be covered
        key_principles = ["autonomy", "beneficence", "non-maleficence", "justice"]
        
        # Get ethical principles mentioned in the final consensus
        mentioned_principles = final_consensus.get("ethical_principles", [])
        
        # Count how many key principles are mentioned
        principle_count = sum(1 for principle in key_principles if principle in mentioned_principles)
        
        # Calculate coverage score
        coverage_score = principle_count / len(key_principles)
        
        return coverage_score
    
    def _evaluate_reasoning_quality(
        self,
        final_consensus: Dict[str, Any],
        agent_responses: List[Dict[str, Any]]
    ) -> float:
        """
        Evaluate the quality of ethical reasoning.
        
        Args:
            final_consensus: Final consensus dictionary
            agent_responses: List of agent responses
            
        Returns:
            Score between 0.0 and 1.0
        """
        # This is a simplified implementation
        # A more comprehensive implementation would use NLP techniques
        
        # Check if recommendation is present and non-empty
        recommendation = final_consensus.get("recommendation", "")
        if not recommendation:
            return 0.0
        
        # Simple heuristics for reasoning quality
        quality_score = 0.0
        
        # 1. Length of recommendation (as a proxy for depth)
        if len(recommendation) > 500:
            quality_score += 0.2
        elif len(recommendation) > 200:
            quality_score += 0.1
        
        # 2. Use of reasoning terms
        reasoning_terms = ["because", "therefore", "given that", "this implies", "consequently"]
        reasoning_term_count = sum(1 for term in reasoning_terms if term in recommendation.lower())
        quality_score += min(0.3, reasoning_term_count * 0.1)
        
        # 3. Multi-perspective consideration
        if "however," in recommendation.lower() or "on the other hand," in recommendation.lower():
            quality_score += 0.2
        
        # 4. Explicit ethical analysis
        if "ethical" in recommendation.lower() and "principle" in recommendation.lower():
            quality_score += 0.1
        
        # 5. Nuanced approach (not black and white)
        nuance_terms = ["balance", "weigh", "consider", "tension", "dilemma"]
        nuance_term_count = sum(1 for term in nuance_terms if term in recommendation.lower())
        quality_score += min(0.2, nuance_term_count * 0.05)
        
        return min(1.0, quality_score)
    
    def _evaluate_evidence_usage(self, final_consensus: Dict[str, Any], case_study: str) -> float:
        """
        Evaluate the usage of evidence from the case study.
        
        Args:
            final_consensus: Final consensus dictionary
            case_study: Case study text
            
        Returns:
            Score between 0.0 and 1.0
        """
        recommendation = final_consensus.get("recommendation", "").lower()
        case_study_lower = case_study.lower()
        
        # Extract key facts from case study
        # This is a simplified approach - a real implementation would use NLP
        key_terms = []
        
        # Get lines with facts from case study
        case_lines = case_study.split("\n")
        for line in case_lines:
            if ":" in line and not line.strip().endswith(":"):
                key_terms.extend([term.strip().lower() for term in line.split(":")[1].split(",")])
        
        # Count how many key terms are referenced in the recommendation
        referenced_count = sum(1 for term in key_terms if term in recommendation and len(term) > 5)
        
        # Calculate evidence usage score
        evidence_score = min(1.0, referenced_count / max(5, len(key_terms) / 3))
        
        return evidence_score
    
    def _evaluate_stakeholder_consideration(
        self,
        final_consensus: Dict[str, Any],
        case_study: str
    ) -> float:
        """
        Evaluate the consideration of all stakeholders.
        
        Args:
            final_consensus: Final consensus dictionary
            case_study: Case study text
            
        Returns:
            Score between 0.0 and 1.0
        """
        recommendation = final_consensus.get("recommendation", "").lower()
        
        # Identify stakeholders in the case study
        # This is a simplified approach - a real implementation would use NLP
        stakeholders = ["patient", "family", "medical team", "physician", "nurse", "hospital"]
        
        # Check which stakeholders are mentioned in the recommendation
        mentioned_count = sum(1 for stakeholder in stakeholders if stakeholder in recommendation)
        
        # Calculate stakeholder consideration score
        stakeholder_score = mentioned_count / len(stakeholders)
        
        return stakeholder_score
    
    def _evaluate_practical_applicability(self, final_consensus: Dict[str, Any]) -> float:
        """
        Evaluate the practical applicability of the recommendation.
        
        Args:
            final_consensus: Final consensus dictionary
            
        Returns:
            Score between 0.0 and 1.0
        """
        recommendation = final_consensus.get("recommendation", "").lower()
        
        # Check for actionable elements
        action_terms = ["should", "recommend", "suggest", "propose", "step", "approach", "strategy"]
        action_count = sum(1 for term in action_terms if term in recommendation)
        
        # Check for implementation details
        implementation_terms = ["implement", "communicate", "discuss", "meeting", "schedule", "document"]
        implementation_count = sum(1 for term in implementation_terms if term in recommendation)
        
        # Check for timeline or process elements
        process_terms = ["first", "then", "next", "follow up", "review", "evaluate"]
        process_count = sum(1 for term in process_terms if term in recommendation)
        
        # Calculate practical applicability score
        applicability_score = min(1.0, (action_count * 0.4 + implementation_count * 0.3 + process_count * 0.3) / 5)
        
        return applicability_score
    
    def _identify_strengths(
        self,
        agent_responses: List[Dict[str, Any]],
        final_consensus: Dict[str, Any]
    ) -> List[str]:
        """
        Identify strengths of the deliberation.
        
        Args:
            agent_responses: List of agent responses
            final_consensus: Final consensus dictionary
            
        Returns:
            List of strengths
        """
        strengths = []
        
        # Check for principle coverage
        if "ethical_principles" in final_consensus and len(final_consensus["ethical_principles"]) >= 3:
            strengths.append("Strong coverage of ethical principles")
        
        # Check for comprehensive recommendation
        if "recommendation" in final_consensus and len(final_consensus["recommendation"]) > 300:
            strengths.append("Comprehensive recommendation")
        
        # Check for confidence level
        if "confidence" in final_consensus and final_consensus["confidence"] > 0.7:
            strengths.append("High confidence in recommendation")
        
        # Check for practical considerations
        recommendation = final_consensus.get("recommendation", "").lower()
        if "implement" in recommendation or "approach" in recommendation:
            strengths.append("Includes practical implementation guidance")
        
        return strengths
    
    def _identify_areas_for_improvement(
        self,
        agent_responses: List[Dict[str, Any]],
        final_consensus: Dict[str, Any]
    ) -> List[str]:
        """
        Identify areas for improvement in the deliberation.
        
        Args:
            agent_responses: List of agent responses
            final_consensus: Final consensus dictionary
            
        Returns:
            List of areas for improvement
        """
        improvements = []
        
        # Check for principle coverage
        principles = final_consensus.get("ethical_principles", [])
        if "autonomy" not in principles:
            improvements.append("Consider patient autonomy more explicitly")
        if "justice" not in principles:
            improvements.append("Address justice/fairness considerations")
        
        # Check for recommendation comprehensiveness
        recommendation = final_consensus.get("recommendation", "")
        if len(recommendation) < 200:
            improvements.append("Provide more detailed recommendation")
        
        # Check for stakeholder consideration
        if "patient" not in recommendation.lower() and "family" not in recommendation.lower():
            improvements.append("Consider patient and family perspectives")
        if "team" not in recommendation.lower() and "staff" not in recommendation.lower():
            improvements.append("Consider healthcare team perspectives")
        
        # Check for practical applicability
        if "implement" not in recommendation.lower() and "approach" not in recommendation.lower():
            improvements.append("Add more practical implementation guidance")
        
        return improvements
    
    def _calculate_innovation_metrics(
        self,
        agent_responses: List[Dict[str, Any]],
        final_consensus: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate innovation metrics for the deliberation.
        
        Args:
            agent_responses: List of agent responses
            final_consensus: Final consensus dictionary
            
        Returns:
            Dictionary of innovation metrics
        """
        # Extract all agent response texts
        response_texts = [response.get("response", "") for response in agent_responses]
        
        # Novelty: Check for unique words/terms across responses
        all_words = set()
        unique_words_per_response = []
        
        for response in response_texts:
            words = set(response.lower().split())
            unique_words_per_response.append(words)
            all_words.update(words)
        
        # Calculate average uniqueness
        avg_unique_ratio = sum(len(words) / len(all_words) for words in unique_words_per_response) / len(unique_words_per_response) if unique_words_per_response else 0
        
        # Diversity: Check for diversity of perspectives
        # Simple proxy - count responses mentioning different principles
        principle_keywords = {
            "autonomy": ["autonomy", "self-determination", "informed consent"],
            "beneficence": ["beneficence", "best interest", "patient welfare"],
            "non-maleficence": ["non-maleficence", "harm", "do no harm"],
            "justice": ["justice", "fairness", "equity"]
        }
        
        perspective_diversity = 0.0
        for response in response_texts:
            principles_mentioned = set()
            for principle, keywords in principle_keywords.items():
                if any(keyword in response.lower() for keyword in keywords):
                    principles_mentioned.add(principle)
            perspective_diversity += len(principles_mentioned) / len(principle_keywords)
        
        perspective_diversity /= len(response_texts) if response_texts else 1
        
        # Calculate coherence as a measure of how well responses build on each other
        # Simple proxy - consistency in ethical principles mentioned
        coherence = 0.0
        if len(unique_words_per_response) > 1:
            overlap_ratios = []
            for i in range(len(unique_words_per_response) - 1):
                overlap = len(unique_words_per_response[i].intersection(unique_words_per_response[i+1]))
                total = len(unique_words_per_response[i].union(unique_words_per_response[i+1]))
                if total > 0:
                    overlap_ratios.append(overlap / total)
            coherence = sum(overlap_ratios) / len(overlap_ratios) if overlap_ratios else 0
        
        return {
            "novelty": 1.0 - avg_unique_ratio,  # Higher novelty = lower overlap
            "perspective_diversity": perspective_diversity,
            "coherence": coherence
        }
    
    def _compare_to_benchmark(
        self,
        evaluation_results: Dict[str, Any],
        benchmark_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare evaluation results to benchmark data.
        
        Args:
            evaluation_results: Dictionary of evaluation results
            benchmark_data: Dictionary of benchmark data
            
        Returns:
            Dictionary of benchmark comparison results
        """
        comparison = {}
        
        # Compare overall score
        benchmark_overall = benchmark_data.get("overall_score", 0.0)
        current_overall = evaluation_results.get("overall_score", 0.0)
        comparison["overall_score_delta"] = current_overall - benchmark_overall
        
        # Compare component scores
        component_deltas = {}
        benchmark_components = benchmark_data.get("component_scores", {})
        current_components = evaluation_results.get("component_scores", {})
        
        for component, score in current_components.items():
            benchmark_score = benchmark_components.get(component, 0.0)
            component_deltas[component] = score - benchmark_score
        
        comparison["component_score_deltas"] = component_deltas
        
        # Calculate percentile if we have a distribution of benchmark scores
        if "score_distribution" in benchmark_data:
            distribution = benchmark_data["score_distribution"]
            percentile = sum(1 for score in distribution if score < current_overall) / len(distribution)
            comparison["percentile"] = percentile
        
        return comparison
    
    def _save_evaluation_results(self, evaluation_results: Dict[str, Any]) -> str:
        """
        Save evaluation results to a file.
        
        Args:
            evaluation_results: Dictionary of evaluation results
            
        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"evaluation_{timestamp}.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_results, f, indent=2)
        
        logger.info(f"Saved evaluation results to {output_path}")
        return output_path 