"""
Command Line Interface for ConsultAI.
Provides a user-friendly interface for running the deliberation pipeline.
"""

import argparse
import json
import logging
import asyncio
from pathlib import Path
from typing import List, Optional

from consultai.utils.pipeline_manager import PipelineManager
from consultai.config.model_manager import ModelTier

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="ConsultAI - Ethical Deliberation System",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Configuration file
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration JSON file"
    )
    
    # Individual arguments
    parser.add_argument(
        "--model-tier",
        type=str,
        choices=["economy", "balanced", "performance"],
        default="economy",
        help="Model tier to use"
    )
    
    parser.add_argument(
        "--case-type",
        type=str,
        choices=["autonomy", "justice", "beneficence", "resource_allocation"],
        default="autonomy",
        help="Type of case study to analyze"
    )
    
    parser.add_argument(
        "--roles",
        nargs="+",
        default=["attending_physician", "nurse_manager"],
        help="Space-separated list of agent roles"
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
        help="Require confirmation for API calls"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/deliberations",
        help="Directory for saving results"
    )
    
    parser.add_argument(
        "--case-study-path",
        type=str,
        help="Path to custom case study file"
    )
    
    return parser.parse_args()

def load_config(config_path: str) -> dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config file: {e}")
        raise

async def run_pipeline(config: dict) -> None:
    """
    Run the deliberation pipeline with given configuration.
    
    Args:
        config: Configuration dictionary
    """
    try:
        # Initialize pipeline manager
        pipeline = PipelineManager(
            model_tier=config["model_tier"],
            require_confirmation=config.get("require_confirmation", True),
            max_concurrent=config.get("max_concurrent", 3)
        )
        
        # Run case study
        results = await pipeline.run_autonomy_case(
            case_study_path=config.get("case_study_path"),
            roles=config.get("roles"),
            max_rounds=config.get("max_rounds", 3),
            max_concurrent=config.get("max_concurrent", 3),
            require_confirmation=config.get("require_confirmation", True)
        )
        
        # Save results
        output_dir = Path(config.get("output_dir", "output/deliberations"))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"results_{results['start_time']}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nDeliberation Summary:")
        logger.info(f"Case Type: {config['case_type']}")
        logger.info(f"Model Tier: {config['model_tier']}")
        logger.info(f"Total Rounds: {len(results['rounds'])}")
        logger.info(f"Consensus Reached: {results['final_consensus']['status']}")
        logger.info(f"Total Cost: ${results['performance_metrics']['api_metrics']['total_cost_usd']:.4f}")
        
    except Exception as e:
        logger.error(f"Error running pipeline: {e}")
        raise

async def main_async():
    """Main async function."""
    args = parse_args()
    
    # Load configuration
    if args.config:
        config = load_config(args.config)
    else:
        # Use command line arguments
        config = {
            "model_tier": args.model_tier,
            "case_type": args.case_type,
            "roles": args.roles,
            "max_rounds": args.max_rounds,
            "max_concurrent": args.max_concurrent,
            "require_confirmation": args.require_confirmation,
            "output_dir": args.output_dir,
            "case_study_path": args.case_study_path
        }
    
    # Print configuration summary
    print("\n" + "="*80)
    print("CONFIRM PIPELINE EXECUTION")
    print("="*80)
    for key, value in config.items():
        print(f"{key}: {value}")
    print("="*80 + "\n")
    
    # Get user confirmation
    confirm = input("Proceed with this pipeline execution? (y/n): ")
    if confirm.lower() != 'y':
        print("Pipeline execution cancelled.")
        return
    
    # Run pipeline
    await run_pipeline(config)

def main():
    """Main entry point."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 