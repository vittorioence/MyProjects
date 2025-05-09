"""
ConsultAI Pipeline Runner
This script provides a flexible interface for running ethical deliberations with customizable parameters.
"""

import argparse
import json
import logging
import asyncio
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from consultai.utils.pipeline_manager import PipelineManager
from consultai.config.model_manager import ModelTier
from consultai.config.dashboard import CaseStudyType
from consultai.utils.visualization import DeliberationVisualizer
from consultai.models.evaluation import DeliberationEvaluator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("output", "logs", f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")),
        logging.StreamHandler()
    ]
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
    output_dir: Optional[str] = None,
    generate_visualizations: bool = True,
    evaluate_results: bool = True,
    web_server: bool = False,
    web_port: int = 8000
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
        output_dir: Directory to save output
        generate_visualizations: Whether to generate visualizations
        evaluate_results: Whether to evaluate results
        web_server: Whether to start a web server to view results
        web_port: Port to use for web server
        
    Returns:
        Dictionary containing deliberation results
    """
    # Create output directory if it doesn't exist
    if output_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join("output", "deliberations", f"{case_type}_{timestamp}")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "visualizations"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "evaluations"), exist_ok=True)
    
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
    
    # Load case study text
    case_study_text = ""
    if custom_case_text:
        case_study_text = custom_case_text
    elif case_study_path:
        with open(case_study_path, 'r', encoding='utf-8') as f:
            case_study_text = f.read()
    
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
    elif case_type == "resource_allocation":
        results = await pipeline.run_resource_allocation_case(
            roles=roles,
            max_rounds=max_rounds,
            max_concurrent=max_concurrent,
            require_confirmation=False,  # Already confirmed at top level
            case_study_path=case_study_path,
            custom_case_text=custom_case_text
        )
    else:
        raise ValueError(f"Unknown case type: {case_type}")
    
    # Save raw results
    results_path = os.path.join(output_dir, "results.json")
    save_results(results, results_path)
    logger.info(f"Saved raw results to {results_path}")
    
    # Generate visualizations if requested
    if generate_visualizations:
        try:
            visualizer = DeliberationVisualizer(output_dir=os.path.join(output_dir, "visualizations"))
            
            # Generate HTML report
            html_path = visualizer.generate_html_report(
                deliberation_results=results,
                case_study=case_study_text
            )
            logger.info(f"Generated HTML report: {html_path}")
            
            # Generate agreement matrix
            matrix_path = visualizer.generate_agreement_matrix(
                deliberation_results=results
            )
            logger.info(f"Generated agreement matrix: {matrix_path}")
            
            # Add visualization paths to results
            results["visualization_paths"] = {
                "html_report": html_path,
                "agreement_matrix": matrix_path
            }
        except Exception as e:
            logger.error(f"Error generating visualizations: {e}")
    
    # Evaluate results if requested
    if evaluate_results:
        try:
            evaluator = DeliberationEvaluator(output_dir=os.path.join(output_dir, "evaluations"))
            
            # Load benchmark data if available
            benchmark_path = os.path.join("data", "benchmarks", f"{case_type}_benchmark.json")
            benchmark_data = None
            
            if os.path.exists(benchmark_path):
                with open(benchmark_path, 'r', encoding='utf-8') as f:
                    benchmark_data = json.load(f)
            
            # Evaluate deliberation
            evaluation_results = evaluator.evaluate_deliberation(
                deliberation_results=results,
                case_study=case_study_text,
                benchmark_data=benchmark_data
            )
            
            # Add evaluation results to results
            results["evaluation"] = evaluation_results
            
            logger.info(f"Overall evaluation score: {evaluation_results['overall_score']:.2f}")
        except Exception as e:
            logger.error(f"Error evaluating results: {e}")
    
    # Start web server if requested
    if web_server:
        try:
            import http.server
            import socketserver
            import threading
            import webbrowser
            
            # Create a custom handler to serve files from the output directory
            class CustomHandler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=output_dir, **kwargs)
            
            # Start server in a separate thread
            handler = CustomHandler
            with socketserver.TCPServer(("", web_port), handler) as httpd:
                server_thread = threading.Thread(target=httpd.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                
                logger.info(f"Started web server at http://localhost:{web_port}")
                
                # Open browser
                webbrowser.open(f"http://localhost:{web_port}/visualizations/")
                
                # Wait for user to exit
                input("Press Enter to stop the server and exit...")
        except Exception as e:
            logger.error(f"Error starting web server: {e}")
    
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
        "--output-dir",
        type=str,
        help="Directory to save output"
    )
    
    parser.add_argument(
        "--no-visualizations",
        action="store_true",
        help="Disable visualization generation"
    )
    
    parser.add_argument(
        "--no-evaluation",
        action="store_true",
        help="Disable result evaluation"
    )
    
    parser.add_argument(
        "--web-server",
        action="store_true",
        help="Start a web server to view results"
    )
    
    parser.add_argument(
        "--web-port",
        type=int,
        default=8000,
        help="Port to use for web server"
    )
    
    args = parser.parse_args()
    
    # Load configuration from file if provided
    if args.config:
        config = load_config(args.config)
        # Override command-line arguments with config values
        for key, value in config.items():
            if hasattr(args, key.replace("-", "_")) and not getattr(args, key.replace("-", "_")):
                setattr(args, key.replace("-", "_"), value)
    
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
        output_dir=args.output_dir,
        generate_visualizations=not args.no_visualizations,
        evaluate_results=not args.no_evaluation,
        web_server=args.web_server,
        web_port=args.web_port
    )
    
    # Print summary
    print("\nDeliberation Summary:")
    print(f"Case Type: {args.case_type}")
    print(f"Model Tier: {args.model_tier}")
    print(f"Total Rounds: {results['case_summary']['total_rounds']}")
    print(f"Consensus Reached: {results['case_summary']['consensus_reached']}")
    
    if "performance_scores" in results and "token_usage" in results["performance_scores"]:
        print(f"Total Cost: ${results['performance_scores']['token_usage']['total_cost']:.4f}")
    
    if "evaluation" in results:
        print(f"\nEvaluation Results:")
        print(f"Overall Score: {results['evaluation']['overall_score']:.2f}/1.00")
        
        if "strengths" in results["evaluation"]:
            print("\nStrengths:")
            for strength in results["evaluation"]["strengths"]:
                print(f"- {strength}")
        
        if "areas_for_improvement" in results["evaluation"]:
            print("\nAreas for Improvement:")
            for area in results["evaluation"]["areas_for_improvement"]:
                print(f"- {area}")
    
    if "visualization_paths" in results:
        print("\nVisualization Paths:")
        for name, path in results["visualization_paths"].items():
            print(f"- {name}: {path}")

def main():
    """Entry point for the script."""
    # Create necessary directories
    os.makedirs("output/logs", exist_ok=True)
    os.makedirs("output/deliberations", exist_ok=True)
    os.makedirs("output/evaluations", exist_ok=True)
    os.makedirs("output/visualizations", exist_ok=True)
    
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 