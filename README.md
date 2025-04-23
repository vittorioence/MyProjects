# ConsultAI Project

ConsultAI is an advanced ethical deliberation system that leverages AI agents to analyze and discuss complex healthcare scenarios.

## Features

- Multi-agent ethical deliberation system
- Support for various healthcare case studies
- Configurable model tiers for cost optimization
- Parallel processing of agent responses
- Comprehensive performance tracking
- Built-in innovation metrics

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ConsultAI_Project.git
cd ConsultAI_Project
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Unix/MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
# Create .env file
cp .env.example .env
# Edit .env with your API key
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # or your custom endpoint
```

## Configuration

Create a `config.json` file in the project root to configure your deliberation session. Here's an example:

```json
{
    "model_tier": "economy",
    "case_type": "autonomy",
    "roles": [
        "attending_physician",
        "nurse_manager",
        "ethicist",
        "patient_advocate"
    ],
    "max_rounds": 3,
    "max_concurrent": 3,
    "require_confirmation": true,
    "output_dir": "output/deliberations",
    "case_study_path": "data/case_studies/autonomy/case1.txt",
    "model": {
        "name": "gpt-4.1-2025-04-14",
        "temperature": 0.7,
        "max_tokens": 4000
    },
    "performance": {
        "track_token_usage": true,
        "track_response_times": true,
        "track_costs": true,
        "cost_threshold": 1.0
    }
}
```

### Configuration Options

#### Basic Settings
- `model_tier`: Choose from "economy", "balanced", or "performance"
- `case_type`: Type of case study ("autonomy", "justice", "beneficence", etc.)
- `roles`: List of agent roles to participate in the deliberation
- `max_rounds`: Maximum number of deliberation rounds
- `max_concurrent`: Maximum number of concurrent API requests
- `require_confirmation`: Whether to require confirmation for API calls
- `output_dir`: Directory for saving results
- `case_study_path`: Path to custom case study file

#### Model Settings
- `name`: Model identifier (default: "gpt-4.1-2025-04-14")
- `temperature`: Model temperature (0.0-1.0)
- `max_tokens`: Maximum tokens per response

#### Performance Settings
- `track_token_usage`: Whether to track token usage
- `track_response_times`: Whether to track response times
- `track_costs`: Whether to track costs
- `cost_threshold`: Maximum cost threshold in USD

### Model Tiers

The system supports three model tiers:
1. Economy (Default)
   - Model: gpt-4.1-2025-04-14
   - Input cost: $0.003 per 1K tokens
   - Output cost: $0.012 per 1K tokens
   - Best for: Cost-effective general analysis

2. Balanced
   - Same model with balanced parameters
   - Best for: Day-to-day operations

3. Performance
   - Same model with optimized parameters
   - Best for: Critical decision-making

## Usage

1. Create your configuration file:
```bash
# Copy the example config
cp config.example.json config.json
# Edit the config file with your settings
```

2. Run the pipeline:
```bash
python run_pipeline.py --config config.json
```

The system will:
1. Load your configuration
2. Initialize the specified case study
3. Set up the agent roles
4. Run the deliberation process
5. Save results to the specified output directory

## Output Structure

The system generates structured output including:
- Deliberation summary
- Agent responses
- Performance metrics
- Cost analysis

Example output location: `output/deliberations/YYYY-MM-DD_HH-MM-SS/`

### Output Files
- `summary.json`: Overall deliberation results
- `metrics.json`: Performance and cost metrics
- `agent_responses/`: Individual agent responses

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 