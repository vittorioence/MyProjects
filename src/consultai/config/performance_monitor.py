"""
Performance monitoring and configuration module for ConsultAI.
This module provides tools for managing API settings, tracking performance metrics,
and visualizing results.
"""

import os
import json
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Tuple

# Import configuration from the main config module
from consultai.config.config import (
    API_CONFIG,
    TOKEN_CONFIG,
    METRICS_CONFIG,
    VISUALIZATION_CONFIG,
    get_api_config,
    get_token_config,
    get_metrics_config,
    get_visualization_config
)

# Load environment variables
load_dotenv()

class PerformanceMonitor:
    """Tracks and analyzes performance metrics for API calls."""
    
    def __init__(self):
        self.metrics = {
            "api_calls": [],
            "token_usage": [],
            "response_times": [],
            "costs": [],
            "errors": [],
            "start_time": time.time(),
        }
        self.output_directory = VISUALIZATION_CONFIG["output_directory"]
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Set matplotlib style with error handling
        try:
            plt.style.use(VISUALIZATION_CONFIG["chart_style"])
        except Exception as e:
            print(f"Warning: Could not set matplotlib style '{VISUALIZATION_CONFIG['chart_style']}': {e}")
            print("Using default style instead.")
            plt.style.use("default")
    
    def log_api_call(self, 
                     input_tokens: int, 
                     output_tokens: int, 
                     response_time_ms: float, 
                     error: Optional[str] = None) -> None:
        """Log an API call with its metrics."""
        timestamp = datetime.datetime.now()
        model = API_CONFIG["model_name"]
        
        # Calculate cost
        input_cost = input_tokens * TOKEN_CONFIG[model]["input_token_cost"]
        output_cost = output_tokens * TOKEN_CONFIG[model]["output_token_cost"]
        total_cost = input_cost + output_cost
        
        # Record metrics
        self.metrics["api_calls"].append({
            "timestamp": timestamp,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "response_time_ms": response_time_ms,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost,
            "error": error
        })
        
        # Update aggregated metrics
        self.metrics["token_usage"].append(input_tokens + output_tokens)
        self.metrics["response_times"].append(response_time_ms)
        self.metrics["costs"].append(total_cost)
        if error:
            self.metrics["errors"].append(error)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of performance metrics."""
        if not self.metrics["api_calls"]:
            return {
                "total_calls": 0,
                "avg_response_time_ms": 0,
                "total_tokens": 0,
                "total_cost": 0,
                "error_rate": 0
            }
        
        total_calls = len(self.metrics["api_calls"])
        avg_response_time = sum(self.metrics["response_times"]) / total_calls
        total_tokens = sum(self.metrics["token_usage"])
        total_cost = sum(self.metrics["costs"])
        error_rate = len(self.metrics["errors"]) / total_calls if total_calls > 0 else 0
        
        return {
            "total_calls": total_calls,
            "avg_response_time_ms": avg_response_time,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "error_rate": error_rate
        }
    
    def estimate_cost(self, 
                      num_calls: int, 
                      avg_input_tokens: int = TOKEN_CONFIG["estimated_input_tokens_per_message"],
                      avg_output_tokens: int = TOKEN_CONFIG["estimated_output_tokens_per_response"]) -> Dict[str, float]:
        """Estimate the cost for a given number of API calls."""
        model = API_CONFIG["model_name"]
        
        input_cost = num_calls * avg_input_tokens * TOKEN_CONFIG[model]["input_token_cost"]
        output_cost = num_calls * avg_output_tokens * TOKEN_CONFIG[model]["output_token_cost"]
        total_cost = input_cost + output_cost
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        }
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text."""
        # Simple estimation: ~4 characters per token
        return len(text) // 4
    
    def visualize_metrics(self) -> None:
        """Generate visualizations of performance metrics."""
        if not self.metrics["api_calls"]:
            print("No metrics to visualize.")
            return
        
        # Convert metrics to DataFrame
        df = pd.DataFrame(self.metrics["api_calls"])
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # Create visualizations
        self._plot_response_times(df)
        self._plot_token_usage(df)
        self._plot_costs(df)
        self._plot_error_rate(df)
        self._plot_cumulative_metrics(df)
    
    def _plot_response_times(self, df: pd.DataFrame) -> None:
        """Plot response times over time."""
        plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])
        plt.plot(df["timestamp"], df["response_time_ms"], marker="o", linestyle="-")
        plt.title("API Response Times")
        plt.xlabel("Time")
        plt.ylabel("Response Time (ms)")
        plt.grid(True)
        plt.savefig(self.output_directory / "response_times.png", format=VISUALIZATION_CONFIG["save_format"])
        plt.close()
    
    def _plot_token_usage(self, df: pd.DataFrame) -> None:
        """Plot token usage over time."""
        plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])
        plt.plot(df["timestamp"], df["total_tokens"], marker="o", linestyle="-")
        plt.title("Token Usage")
        plt.xlabel("Time")
        plt.ylabel("Tokens")
        plt.grid(True)
        plt.savefig(self.output_directory / "token_usage.png", format=VISUALIZATION_CONFIG["save_format"])
        plt.close()
    
    def _plot_costs(self, df: pd.DataFrame) -> None:
        """Plot costs over time."""
        plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])
        plt.plot(df["timestamp"], df["total_cost"], marker="o", linestyle="-")
        plt.title("API Costs")
        plt.xlabel("Time")
        plt.ylabel("Cost ($)")
        plt.grid(True)
        plt.savefig(self.output_directory / "costs.png", format=VISUALIZATION_CONFIG["save_format"])
        plt.close()
    
    def _plot_error_rate(self, df: pd.DataFrame) -> None:
        """Plot error rate over time."""
        # Calculate error rate in windows
        window_size = min(10, len(df))
        if window_size < 1:
            return
        
        df["has_error"] = df["error"].notna().astype(int)
        error_rate = df["has_error"].rolling(window=window_size).mean()
        
        plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])
        plt.plot(df["timestamp"], error_rate, marker="o", linestyle="-")
        plt.title("Error Rate")
        plt.xlabel("Time")
        plt.ylabel("Error Rate")
        plt.grid(True)
        plt.savefig(self.output_directory / "error_rate.png", format=VISUALIZATION_CONFIG["save_format"])
        plt.close()
    
    def _plot_cumulative_metrics(self, df: pd.DataFrame) -> None:
        """Plot cumulative metrics over time."""
        plt.figure(figsize=VISUALIZATION_CONFIG["figure_size"])
        
        # Create subplots
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=VISUALIZATION_CONFIG["figure_size"])
        
        # Cumulative tokens
        ax1.plot(df["timestamp"], df["total_tokens"].cumsum(), marker="o", linestyle="-")
        ax1.set_title("Cumulative Token Usage")
        ax1.set_xlabel("Time")
        ax1.set_ylabel("Tokens")
        ax1.grid(True)
        
        # Cumulative cost
        ax2.plot(df["timestamp"], df["total_cost"].cumsum(), marker="o", linestyle="-", color="green")
        ax2.set_title("Cumulative Cost")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Cost ($)")
        ax2.grid(True)
        
        # API calls over time
        ax3.plot(df["timestamp"], range(1, len(df) + 1), marker="o", linestyle="-", color="purple")
        ax3.set_title("Cumulative API Calls")
        ax3.set_xlabel("Time")
        ax3.set_ylabel("Number of Calls")
        ax3.grid(True)
        
        plt.tight_layout()
        plt.savefig(self.output_directory / "cumulative_metrics.png", format=VISUALIZATION_CONFIG["save_format"])
        plt.close()
    
    def save_metrics(self, filename: str = "performance_metrics.json") -> None:
        """Save metrics to a JSON file."""
        # Convert datetime objects to strings
        metrics_copy = self.metrics.copy()
        for i, call in enumerate(metrics_copy["api_calls"]):
            metrics_copy["api_calls"][i]["timestamp"] = call["timestamp"].isoformat()
        
        with open(self.output_directory / filename, "w") as f:
            json.dump(metrics_copy, f, indent=2)
    
    def load_metrics(self, filename: str = "performance_metrics.json") -> None:
        """Load metrics from a JSON file."""
        try:
            with open(self.output_directory / filename, "r") as f:
                metrics = json.load(f)
            
            # Convert string timestamps back to datetime objects
            for i, call in enumerate(metrics["api_calls"]):
                metrics["api_calls"][i]["timestamp"] = datetime.datetime.fromisoformat(call["timestamp"])
            
            self.metrics = metrics
        except FileNotFoundError:
            print(f"Metrics file {filename} not found.")
        except Exception as e:
            print(f"Error loading metrics: {e}")

# --- Usage Example ---
if __name__ == "__main__":
    # Create a monitor instance
    monitor = PerformanceMonitor()
    
    # Estimate costs for a training run
    estimated_costs = monitor.estimate_cost(
        num_calls=100,
        avg_input_tokens=200,
        avg_output_tokens=800
    )
    
    print("Estimated costs for 100 API calls:")
    print(f"  Input cost: ${estimated_costs['input_cost']:.4f}")
    print(f"  Output cost: ${estimated_costs['output_cost']:.4f}")
    print(f"  Total cost: ${estimated_costs['total_cost']:.4f}")
    
    # Example of logging an API call
    monitor.log_api_call(
        input_tokens=150,
        output_tokens=750,
        response_time_ms=2500,
        error=None
    )
    
    # Get summary
    summary = monitor.get_summary()
    print("\nPerformance Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Save metrics
    monitor.save_metrics()
    
    # Visualize metrics (will only show one data point in this example)
    monitor.visualize_metrics() 