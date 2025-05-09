# ConsultAI API Documentation

This documentation covers the main interfaces and APIs of the ConsultAI system.

## Pipeline Manager API

The primary interface for running ethical deliberations is the `PipelineManager` class.

```python
from consultai.utils.pipeline_manager import PipelineManager

# Initialize the pipeline manager
pipeline = PipelineManager(
    model_tier="balanced",
    require_confirmation=False
)

# Run a specific case type
results = await pipeline.run_autonomy_case(
    roles=["attending_physician", "patient_advocate", "clinical_ethicist"],
    max_rounds=3,
    max_concurrent=3,
    case_study_path="data/case_studies/autonomy/case1.txt"
)
```

### Available Methods

- `run_autonomy_case`: Run a deliberation on an autonomy-focused case
- `run_beneficence_case`: Run a deliberation on a beneficence-focused case
- `run_justice_case`: Run a deliberation on a justice-focused case
- `run_resource_allocation_case`: Run a deliberation on a resource allocation case

## Visualization API

The `DeliberationVisualizer` class provides visualization capabilities.

```python
from consultai.utils.visualization import DeliberationVisualizer

# Initialize the visualizer
visualizer = DeliberationVisualizer(output_dir="output/visualizations")

# Generate HTML report
html_path = visualizer.generate_html_report(
    deliberation_results=results,
    case_study=case_study_text
)

# Generate agreement matrix
matrix_path = visualizer.generate_agreement_matrix(
    deliberation_results=results
)
```

## Evaluation API

The `DeliberationEvaluator` class provides evaluation capabilities.

```python
from consultai.models.evaluation import DeliberationEvaluator

# Initialize the evaluator
evaluator = DeliberationEvaluator(output_dir="output/evaluations")

# Evaluate discussion quality
quality_assessment = evaluator.evaluate_discussion_quality(
    deliberation_results=results,
    case_study=case_study_text
)

# Generate comprehensive evaluation report
report_path = evaluator.generate_evaluation_report(
    deliberation_results=results,
    quality_assessment=quality_assessment
)
```

## Configuration API

The configuration system can be accessed through the `config` module.

```python
from consultai.config.config import load_config, save_config

# Load configuration
config = load_config("config.json")

# Modify configuration
config["model_tier"] = "performance"
config["max_rounds"] = 5

# Save updated configuration
save_config(config, "config.json")
```

## Model API

The model system can be accessed through the `model_manager` module.

```python
from consultai.config.model_manager import ModelTier, get_model_config

# Get model configuration for a specific tier
model_config = get_model_config(ModelTier.BALANCED)

# Access model parameters
model_name = model_config["name"]
temperature = model_config["temperature"]
max_tokens = model_config["max_tokens"]
```

## Role API

The role system can be accessed through the `role_manager` module.

```python
from consultai.config.role_manager import RoleManager

# Initialize the role manager
role_manager = RoleManager()

# Get all available roles
all_roles = role_manager.get_all_roles()

# Get a specific role by ID
physician_role = role_manager.get_role("attending_physician")

# Access role properties
role_name = physician_role["name"]
role_description = physician_role["description"]
system_message = physician_role["system_message"]
``` 