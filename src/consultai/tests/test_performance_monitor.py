"""
Test script for the performance monitoring module.
This script simulates API calls and tests the performance monitoring functionality
without making actual API requests, allowing for low-cost debugging.
"""

import os
import sys
import time
import random
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the module
sys.path.append(str(Path(__file__).parent.parent.parent))

from consultai.config.performance_monitor import PerformanceMonitor, API_CONFIG, TOKEN_CONFIG

class MockAPICall:
    """Simulates an API call without making an actual request."""
    
    def __init__(self, model_name, input_text, max_tokens, temperature):
        self.model_name = model_name
        self.input_text = input_text
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.start_time = None
        self.end_time = None
        self.response = None
        self.error = None
    
    def execute(self):
        """Simulate executing an API call."""
        self.start_time = time.time()
        
        # Simulate API processing time (random between 500ms and 3000ms)
        processing_time = random.uniform(0.5, 3.0)
        time.sleep(processing_time)
        
        # Simulate occasional errors (5% chance)
        if random.random() < 0.05:
            self.error = "API Error: Rate limit exceeded"
            self.end_time = time.time()
            return None
        
        # Generate a mock response
        response_length = min(random.randint(100, self.max_tokens), self.max_tokens)
        self.response = "This is a simulated response with " + " ".join(["word"] * response_length)
        
        self.end_time = time.time()
        return self.response
    
    def get_metrics(self):
        """Get metrics for the simulated API call."""
        if self.start_time is None or self.end_time is None:
            return None
        
        response_time_ms = (self.end_time - self.start_time) * 1000
        
        # Estimate token counts
        input_tokens = len(self.input_text) // 4  # Rough estimate
        output_tokens = len(self.response) // 4 if self.response else 0
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "response_time_ms": response_time_ms,
            "error": self.error
        }

def simulate_training_run(monitor, num_calls=10, batch_size=3):
    """
    Simulate a training run with multiple API calls.
    
    Args:
        monitor: PerformanceMonitor instance
        num_calls: Total number of API calls to simulate
        batch_size: Number of parallel calls to simulate
    """
    print(f"Simulating training run with {num_calls} API calls (batch size: {batch_size})")
    
    # Estimate costs before starting
    estimated_costs = monitor.estimate_cost(
        num_calls=num_calls,
        avg_input_tokens=200,
        avg_output_tokens=800
    )
    
    print("\nEstimated costs:")
    print(f"  Input cost: ${estimated_costs['input_cost_usd']:.4f}")
    print(f"  Output cost: ${estimated_costs['output_cost_usd']:.4f}")
    print(f"  Total cost: ${estimated_costs['total_cost_usd']:.4f}")
    print(f"  Estimated tokens: {estimated_costs['estimated_tokens']}")
    
    # Simulate API calls in batches
    for batch_start in range(0, num_calls, batch_size):
        batch_end = min(batch_start + batch_size, num_calls)
        batch_size_actual = batch_end - batch_start
        
        print(f"\nExecuting batch {batch_start//batch_size + 1}/{(num_calls + batch_size - 1)//batch_size} ({batch_size_actual} calls)")
        
        # Create and execute mock API calls
        mock_calls = []
        for i in range(batch_size_actual):
            input_text = f"This is a simulated input text for API call {batch_start + i + 1}"
            mock_call = MockAPICall(
                model_name=API_CONFIG["model_name"],
                input_text=input_text,
                max_tokens=API_CONFIG["max_tokens"],
                temperature=API_CONFIG["temperature"]
            )
            mock_calls.append(mock_call)
        
        # Execute calls in parallel (simulated)
        for mock_call in mock_calls:
            mock_call.execute()
        
        # Log results
        for mock_call in mock_calls:
            metrics = mock_call.get_metrics()
            if metrics:
                monitor.log_api_call(
                    input_tokens=metrics["input_tokens"],
                    output_tokens=metrics["output_tokens"],
                    response_time_ms=metrics["response_time_ms"],
                    error=metrics["error"]
                )
        
        # Simulate delay between batches
        if batch_end < num_calls:
            delay = API_CONFIG["delay_between_requests"]
            print(f"Waiting {delay} seconds before next batch...")
            time.sleep(delay)
    
    # Get summary after all calls
    summary = monitor.get_summary()
    print("\nPerformance Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Save metrics
    monitor.save_metrics()
    
    # Generate visualizations
    monitor.visualize_metrics()
    
    return summary

def test_different_models():
    """Test performance monitoring with different models."""
    models = ["gpt-4", "gpt-3.5-turbo", "gpt-4.1-nano"]
    results = {}
    
    for model in models:
        print(f"\n{'='*50}")
        print(f"Testing with model: {model}")
        print(f"{'='*50}")
        
        # Create a new monitor for each model
        monitor = PerformanceMonitor()
        
        # Override the model name
        API_CONFIG["model_name"] = model
        
        # Simulate a small training run
        summary = simulate_training_run(monitor, num_calls=5, batch_size=2)
        
        # Store results
        results[model] = summary
    
    # Compare results
    print("\n\nModel Comparison:")
    print(f"{'Model':<15} {'Total Cost ($)':<15} {'Avg Response Time (ms)':<25} {'Error Rate':<15}")
    print("-" * 70)
    
    for model, summary in results.items():
        print(f"{model:<15} {summary['total_cost_usd']:<15.4f} {summary['average_response_time_ms']:<25.2f} {summary['error_rate']:<15.4f}")

def test_token_estimation():
    """Test the token estimation functionality."""
    monitor = PerformanceMonitor()
    
    test_texts = [
        "This is a short text.",
        "This is a medium length text with more words and some repetition of words and phrases.",
        "This is a much longer text with many more words and sentences. It contains various topics and ideas that would typically be found in a longer document. The purpose is to test how well the token estimation works with texts of different lengths and complexities. We want to see if the simple character-based estimation is reasonable for planning purposes."
    ]
    
    print("\nToken Estimation Test:")
    print(f"{'Text Length':<15} {'Estimated Tokens':<20} {'Actual Ratio':<15}")
    print("-" * 50)
    
    for text in test_texts:
        estimated_tokens = monitor.estimate_tokens(text)
        actual_ratio = len(text) / (estimated_tokens * 4)  # Compare to the 4 chars per token assumption
        print(f"{len(text):<15} {estimated_tokens:<20} {actual_ratio:<15.2f}")

def test_cost_estimation():
    """Test the cost estimation functionality."""
    monitor = PerformanceMonitor()
    
    test_scenarios = [
        {"num_calls": 10, "input_tokens": 100, "output_tokens": 500},
        {"num_calls": 100, "input_tokens": 200, "output_tokens": 1000},
        {"num_calls": 1000, "input_tokens": 500, "output_tokens": 2000}
    ]
    
    print("\nCost Estimation Test:")
    print(f"{'Num Calls':<15} {'Input Tokens':<15} {'Output Tokens':<15} {'Total Cost ($)':<15}")
    print("-" * 60)
    
    for scenario in test_scenarios:
        costs = monitor.estimate_cost(
            num_calls=scenario["num_calls"],
            avg_input_tokens=scenario["input_tokens"],
            avg_output_tokens=scenario["output_tokens"]
        )
        print(f"{scenario['num_calls']:<15} {scenario['input_tokens']:<15} {scenario['output_tokens']:<15} {costs['total_cost_usd']:<15.4f}")

def test_visualization():
    """Test the visualization functionality with simulated data."""
    monitor = PerformanceMonitor()
    
    # Generate a variety of simulated API calls
    for i in range(20):
        # Vary the token counts and response times
        input_tokens = random.randint(50, 300)
        output_tokens = random.randint(200, 1200)
        response_time_ms = random.uniform(500, 5000)
        
        # Simulate occasional errors
        error = "API Error: Rate limit exceeded" if random.random() < 0.1 else None
        
        # Log the call
        monitor.log_api_call(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            response_time_ms=response_time_ms,
            error=error
        )
    
    # Generate visualizations
    monitor.visualize_metrics()
    print("\nVisualization test complete. Check the output/visualizations directory for charts.")

def main():
    """Run all tests."""
    print("Starting performance monitor tests...")
    
    # Test token estimation
    test_token_estimation()
    
    # Test cost estimation
    test_cost_estimation()
    
    # Test visualization with simulated data
    test_visualization()
    
    # Test with different models
    test_different_models()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    main() 