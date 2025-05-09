# ConsultAI Project Structure

This document provides an overview of the ConsultAI project structure and organization.

## Directory Organization

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
```

## Key Components

### Core Modules

- **Pipeline Manager**: Central component that orchestrates the entire deliberation process
- **Model Manager**: Handles model configuration and API interactions
- **Role Manager**: Manages the different deliberation participants (agents)
- **Visualization Engine**: Creates interactive visualizations of deliberation results
- **Evaluation Framework**: Assesses the quality of ethical reasoning

### Code Organization

- **Package Organization**: The project follows a modular package structure
- **Configuration Management**: Centralized configuration through the config module
- **Testing Strategy**: Unit tests for core components, integration tests for workflows

## Development Workflow

1. Configure the environment with `.env` file
2. Set up your case study parameters in `config.json`
3. Run the pipeline with `python run_pipeline.py`
4. View results in the `output` directory

## Best Practices

- Follow the existing code style and naming conventions
- Add appropriate documentation for new components
- Add tests for new functionality
- Use type hints for better code quality 