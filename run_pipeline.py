"""
ConsultAI Pipeline Runner
This script provides a flexible interface for running ethical deliberations with customizable parameters.
"""

import argparse
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

from consultai.utils.pipeline_manager import PipelineManager
from consultai.config.model_manager import ModelTier
from consultai.config.dashboard import CaseStudyType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from a JSON file."""
    with open(config_path, 'r') as f:
        return json.load(f)

def save_results(results: Dict[str, Any], output_path: str):
    """Save results to a JSON file."""
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

async def run_pipeline(
    case_type: str = "autonomy",
    model_tier: str = "balanced",
    roles: Optional[List[str]] = None,
    max_rounds: int = 3,
    max_concurrent: int = 3,
    require_confirmation: bool = False,
    case_study_path: Optional[str] = None,
    custom_case_text: Optional[str] = None,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run the ethical deliberation pipeline.
    
    Args:
        case_type: Type of case study to analyze
        model_tier: Model tier to use (economy, balanced, performance)
        roles: List of roles to include in deliberation
        max_rounds: Maximum number of deliberation rounds
        max_concurrent: Maximum number of concurrent API requests
        require_confirmation: Whether to require confirmation before making API requests
        case_study_path: Path to custom case study file
        custom_case_text: Custom case study text
        output_path: Path to save output
        
    Returns:
        Dictionary containing deliberation results
    """
    # Initialize pipeline manager
    pipeline = PipelineManager(
        model_tier=model_tier,
        require_confirmation=require_confirmation
    )
    
    # If confirmation is required, ask once at the top level
    if require_confirmation:
        print("\n" + "=" * 80)
        print("CONFIRM PIPELINE EXECUTION")
        print("=" * 80)
        print(f"Case Type: {case_type}")
        print(f"Model Tier: {model_tier}")
        print(f"Roles: {roles or 'All available roles'}")
        print(f"Max Rounds: {max_rounds}")
        print(f"Max Concurrent Requests: {max_concurrent}")
        print("=" * 80)
        
        while True:
            response = input("\nProceed with this pipeline execution? (y/n): ").lower()
            if response in ['y', 'yes']:
                break
            elif response in ['n', 'no']:
                return {
                    "status": "cancelled",
                    "message": "Pipeline execution cancelled by user"
                }
            else:
                print("Please enter 'y' or 'n'.")
    
    # Run the appropriate case study
    if case_type == "autonomy":
        results = await pipeline.run_autonomy_case(
            roles=roles,
            max_rounds=max_rounds,
            max_concurrent=max_concurrent,
            require_confirmation=False,  # Already confirmed at top level
            case_study_path=case_study_path,
            custom_case_text=custom_case_text
        )
    elif case_type == "beneficence":
        results = await pipeline.run_beneficence_case(
            roles=roles,
            max_rounds=max_rounds,
            max_concurrent=max_concurrent,
            require_confirmation=False,  # Already confirmed at top level
            case_study_path=case_study_path,
            custom_case_text=custom_case_text
        )
    elif case_type == "justice":
        results = await pipeline.run_justice_case(
            roles=roles,
            max_rounds=max_rounds,
            max_concurrent=max_concurrent,
            require_confirmation=False,  # Already confirmed at top level
            case_study_path=case_study_path,
            custom_case_text=custom_case_text
        )
    else:
        raise ValueError(f"Unknown case type: {case_type}")
    
    # Save results if output path is provided
    if output_path:
        save_results(results, output_path)
    
    return results

async def main_async():
    """Command-line interface for running the pipeline."""
    parser = argparse.ArgumentParser(description="Run ConsultAI ethical deliberation pipeline")
    
    # Create a mutually exclusive group for case-type and config
    case_group = parser.add_mutually_exclusive_group(required=True)
    
    case_group.add_argument(
        "--case-type",
        type=str,
        choices=["autonomy", "beneficence", "justice", "resource_allocation"],
        help="Type of case study to analyze"
    )
    
    case_group.add_argument(
        "--config",
        type=str,
        help="Path to configuration file (JSON)"
    )
    
    parser.add_argument(
        "--model-tier",
        type=str,
        default="balanced",
        choices=["economy", "balanced", "performance"],
        help="Model tier to use (economy=GPT-3.5, balanced/performance=GPT-4)"
    )
    
    parser.add_argument(
        "--roles",
        type=str,
        nargs="+",
        help="List of roles to use (defaults to case-specific roles)"
    )
    
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=3,
        help="Maximum number of deliberation rounds"
    )
    
    parser.add_argument(
        "--max-concurrent",
        type=int,
        default=3,
        help="Maximum number of concurrent API requests"
    )
    
    parser.add_argument(
        "--require-confirmation",
        action="store_true",
        help="Require confirmation for API requests"
    )
    
    parser.add_argument(
        "--case-study-path",
        type=str,
        help="Path to custom case study file"
    )
    
    parser.add_argument(
        "--custom-case-text",
        type=str,
        help="Custom case study text"
    )
    
    parser.add_argument(
        "--output-path",
        type=str,
        help="Path to save results"
    )
    
    args = parser.parse_args()
    
    # Load configuration from file if provided
    if args.config:
        config = load_config(args.config)
        # Override command-line arguments with config values
        for key, value in config.items():
            if hasattr(args, key) and not getattr(args, key):
                setattr(args, key, value)
    
    # Run pipeline
    results = await run_pipeline(
        case_type=args.case_type,
        model_tier=args.model_tier,
        roles=args.roles,
        max_rounds=args.max_rounds,
        max_concurrent=args.max_concurrent,
        require_confirmation=args.require_confirmation,
        case_study_path=args.case_study_path,
        custom_case_text=args.custom_case_text,
        output_path=args.output_path
    )
    
    # Print summary
    print("\nDeliberation Summary:")
    print(f"Case Type: {args.case_type}")
    print(f"Model Tier: {args.model_tier}")
    print(f"Total Rounds: {results['case_summary']['total_rounds']}")
    print(f"Consensus Reached: {results['case_summary']['consensus_reached']}")
    print(f"Total Cost: ${results['performance_scores']['token_usage']['total_cost']:.4f}")

def main():
    """Entry point for the script."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 