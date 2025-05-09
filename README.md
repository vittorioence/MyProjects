# ConsultAI Project

ConsultAI is an advanced ethical decision support system that leverages multi-agent technology to analyze and discuss complex medical scenarios, providing ethical decision support for healthcare professionals.

## Key Features

- **Multi-Agent Ethics Discussion System**: Simulates collaborative decision-making among healthcare professionals in different roles
- **Diverse Medical Case Support**: Built-in various types of ethical cases (autonomy, beneficence, justice, resource allocation)
- **Configurable Model Tiers**: Economy, balanced, and performance modes to meet different decision-making scenarios
- **Parallel Agent Response Processing**: Improves system processing efficiency and reduces overall response times
- **Comprehensive Performance Tracking**: Monitors token usage, response times, and costs
- **Ethics Reasoning Quality Assessment**: Automatically evaluates discussion quality and coverage of ethical principles
- **Interactive Visualizations**: Generates intuitive reports and agreement matrices to visualize discussion processes and results
- **Custom Agent Roles**: Supports customization of participants with different professional backgrounds and positions

## Project Structure

```
ConsultAI_Project/
├── data/                        # Data directory
│   ├── benchmarks/              # Benchmark data
│   ├── case_studies/            # Case studies
│   │   ├── autonomy/            # Autonomy cases
│   │   ├── beneficence/         # Beneficence principle cases
│   │   ├── justice/             # Justice principle cases
│   │   └── resource_allocation/ # Resource allocation cases
│   ├── knowledge_base/          # Knowledge base data
│   └── roles/                   # Role definitions
├── docs/                        # Documentation
│   ├── api/                     # API documentation
│   ├── design/                  # Design documents
│   └── poster/                  # Project posters and presentations
├── output/                      # Output directory
│   ├── deliberations/           # Deliberation results
│   ├── evaluations/             # Evaluation results
│   ├── logs/                    # Log files
│   ├── summaries/               # Summaries
│   └── visualizations/          # Visualization outputs
├── src/                         # Source code
│   ├── consultai/               # Core package
│   │   ├── cli/                 # Command-line interface
│   │   ├── config/              # Configuration management
│   │   ├── models/              # Model definitions
│   │   ├── prompts/             # Prompt templates
│   │   ├── tests/               # Unit tests
│   │   └── utils/               # Utilities
│   └── consultai.egg-info/      # Package metadata
├── tests/                       # Tests
├── .env                         # Environment variables
├── config.example.json          # Example configuration
├── config.json                  # Runtime configuration
├── requirements.txt             # Dependencies
├── run_pipeline.py              # Main execution script
└── setup.py                     # Installation script
```

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
pip install -e .  # Install local package in development mode
```

4. Configure environment variables:
```bash
# Create .env file
cp .env.example .env
# Edit .env file and add your API key
# OPENAI_API_KEY=your_api_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1  # Or your custom endpoint
```

## Configuration

Create a `config.json` file in the project root directory to configure your discussion session. Example configuration:

```json
{
    "model_tier": "economy",
    "case_type": "autonomy",
    "roles": [
        "attending_physician",
        "patient_advocate",
        "clinical_ethicist"
    ],
    "max_rounds": 3,
    "max_concurrent": 3,
    "require_confirmation": false,
    "output_dir": "output/deliberations",
    "case_study_path": "data/case_studies/autonomy/case1.txt",
    "generate_visualizations": true,
    "evaluate_results": true,
    "model": {
        "name": "gpt-4.1-nano",
        "temperature": 0.7,
        "max_tokens": 2000
    },
    "performance": {
        "track_token_usage": true,
        "track_response_times": true,
        "track_costs": true,
        "cost_threshold": 0.5
    }
}
```

### Configuration Options

#### Basic Settings
- `model_tier`: Choose "economy", "balanced", or "performance"
- `case_type`: Case type ("autonomy", "justice", "beneficence", "resource_allocation")
- `roles`: List of agent roles participating in the discussion
- `max_rounds`: Maximum number of discussion rounds
- `max_concurrent`: Maximum number of concurrent API requests
- `require_confirmation`: Whether API calls require confirmation
- `output_dir`: Directory to save results
- `case_study_path`: Custom case study file path
- `generate_visualizations`: Whether to generate interactive visualizations
- `evaluate_results`: Whether to evaluate ethics reasoning quality

#### Model Settings
- `name`: Model identifier (e.g., "gpt-4.1-nano", "gpt-3.5-turbo")
- `temperature`: Model temperature (0.0-1.0)
- `max_tokens`: Maximum tokens per response

#### Performance Settings
- `track_token_usage`: Whether to track token usage
- `track_response_times`: Whether to track response times
- `track_costs`: Whether to track costs
- `cost_threshold`: Maximum cost threshold (USD)

## Usage

1. Create a configuration file:
```bash
# Copy example configuration
cp config.example.json config.json
# Edit the configuration file
```

2. Run the pipeline:
```bash
python run_pipeline.py --config config.json
```

3. Advanced options:
```bash
python run_pipeline.py --case-type autonomy --model-tier balanced --roles attending_physician patient_advocate clinical_ethicist --max-rounds 4 --web-server
```

The system will:
1. Load your configuration
2. Initialize the specified case study
3. Set up agent roles
4. Run the discussion process
5. Evaluate ethics reasoning quality
6. Generate interactive visualizations
7. Save all results to the specified output directory
8. Optionally start a web server to view results

## Output Structure

The structured outputs generated by the system include:
- Discussion summaries
- Agent responses
- Performance metrics
- Cost analysis
- Ethics reasoning assessments
- Interactive visualizations

Example output location: `output/deliberations/YYYY-MM-DD_HH-MM-SS/`

### Output Files
- `results.json`: Overall discussion results
- `evaluations/`: Ethics reasoning quality assessments
- `visualizations/`: Interactive visualizations of the discussion
  - `deliberation_report_*.html`: Complete discussion report with timeline visualization
  - `agreement_matrix_*.html`: Visualization of agent agreement

## Custom Role Configuration

You can customize the agent roles used in discussions by creating or modifying role definitions:

1. The system includes pre-configured roles:
   - Attending Physician
   - Nurse Manager
   - Clinical Ethicist
   - Patient Advocate
   - Hospital Administrator
   - Family Representative
   - Healthcare Attorney
   - Chaplain
   - Social Worker

2. Create custom roles by adding to `data/roles/role_definitions.json`:
```json
{
  "role_id": "palliative_care_specialist",
  "name": "Palliative Care Specialist",
  "description": "Expert in end-of-life care and symptom management",
  "system_message": "You are a palliative care specialist with extensive experience in managing symptoms and supporting patients at the end of life...",
  "expertise_areas": ["pain management", "symptom control", "end-of-life care", "psychosocial support"],
  "stakeholder_perspective": "healthcare provider",
  "memory_size": 10,
  "token_limit": 4000
}
```

## Evaluation Framework

The system includes a comprehensive evaluation framework to assess the quality of ethical reasoning:

### Evaluation Criteria
- **Ethical Principles Coverage**: Analyzes how well the discussion covers key ethical principles
- **Reasoning Quality**: Evaluates the depth and coherence of ethical reasoning
- **Evidence Use**: Measures how effectively the discussion utilizes case evidence
- **Stakeholder Consideration**: Assesses consideration of different stakeholder perspectives
- **Practicality**: Evaluates the practicality of recommendations

### Benchmark Comparisons
The system can compare discussion results against benchmarks to evaluate relative performance. Benchmark data is stored in `data/benchmarks/`.

## Visualization System

The visualization system provides interactive views of the discussion process:

### Visualization Types
- **Discussion Report**: Complete HTML report with tabs for case details, agent responses, and final consensus
- **Agreement Matrix**: Heatmap visualization showing the level of agreement between different agents
- **Timeline Visualization**: Chart showing the evolution of agent confidence and opinions across discussion rounds

## Testing Mode

ConsultAI includes a simulation mode that can simulate API responses without making actual API calls. This is useful for testing the pipeline, visualizations, and other components without using API quotas.

To enable simulation mode:

1. In the configuration, ensure the `mock_mode` parameter is set to `true`:
```python
# In src/consultai/config/config.py
DEFAULT_CONFIG = {
    # ...
    "mock_mode": True,
    # ...
}
```

2. Run the pipeline as normal:
```bash
python run_pipeline.py --config config.json
```

Simulation mode will:
- Skip actual API calls
- Generate simulated responses
- Process the pipeline normally
- Create visualizations and evaluation results

This allows for rapid iteration and testing of system components without using API quotas or waiting for real API responses.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 