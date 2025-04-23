import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from consultai.models.deliberation import run_deliberation
from consultai.config.settings import CASE_STUDIES

def main():
    """
    Main entry point for the ConsultAI application.
    Runs deliberations for all configured case studies.
    """
    # Create output directories if they don't exist
    output_dirs = ['output/logs', 'output/evaluations', 'output/summaries']
    for dir_path in output_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)

    # Run deliberations for each case study
    for case_study_key in CASE_STUDIES:
        print(f"\n\n===== RUNNING DELIBERATION FOR {case_study_key.upper()} =====\n")
        run_deliberation(case_study_key)

if __name__ == "__main__":
    main() 