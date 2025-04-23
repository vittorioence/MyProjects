"""
CLI Dashboard for ConsultAI.
Provides a command-line interface to view and manage system settings.
"""

import click
from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from consultai.config.model_manager import ModelManager, ModelTier
from consultai.config.dashboard import DashboardConfig, CaseStudyType

console = Console()

def display_model_info(model_manager: ModelManager):
    """Display information about available models"""
    table = Table(title="Available Models")
    table.add_column("Model", style="cyan")
    table.add_column("Max Tokens", justify="right")
    table.add_column("Temperature", justify="right")
    table.add_column("Input Cost/1K", justify="right")
    table.add_column("Output Cost/1K", justify="right")
    table.add_column("Capabilities", style="green")
    
    for model_name, config in model_manager.get_available_models().items():
        capabilities = ", ".join(k for k, v in config.capabilities.items() if v)
        table.add_row(
            model_name,
            str(config.max_tokens),
            str(config.temperature),
            f"${config.cost_per_1k_input:.4f}",
            f"${config.cost_per_1k_output:.4f}",
            capabilities
        )
    
    console.print(table)

def display_task_models(model_manager: ModelManager):
    """Display task-specific model recommendations"""
    table = Table(title="Task-Specific Model Recommendations")
    table.add_column("Task", style="cyan")
    table.add_column("Economy", style="yellow")
    table.add_column("Balanced", style="green")
    table.add_column("Performance", style="red")
    
    for task, models in model_manager.get_task_models().items():
        table.add_row(
            task,
            models[ModelTier.ECONOMY],
            models[ModelTier.BALANCED],
            models[ModelTier.PERFORMANCE]
        )
    
    console.print(table)

def display_case_studies(dashboard: DashboardConfig):
    """Display available case studies"""
    table = Table(title="Available Case Studies")
    table.add_column("Type", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Complexity", justify="right")
    table.add_column("Required Roles", style="yellow")
    table.add_column("Principles", style="magenta")
    
    for case_type, config in dashboard.get_available_case_studies().items():
        table.add_row(
            case_type.value,
            config.title,
            str(config.complexity_level),
            ", ".join(config.required_roles),
            ", ".join(config.ethical_principles)
        )
    
    console.print(table)

def display_roles(dashboard: DashboardConfig):
    """Display available roles"""
    table = Table(title="Available Roles")
    table.add_column("Role", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Memory Size", justify="right")
    table.add_column("Token Limit", justify="right")
    table.add_column("Required Capabilities", style="yellow")
    
    for role_name, config in dashboard.get_available_roles().items():
        table.add_row(
            role_name,
            config.description,
            str(config.memory_size),
            str(config.token_limit),
            ", ".join(config.required_capabilities)
        )
    
    console.print(table)

def display_system_settings(dashboard: DashboardConfig):
    """Display current system settings"""
    settings = dashboard.get_system_settings()
    console.print(Panel.fit(
        f"[cyan]Model Tier:[/cyan] {settings['model_tier'].value}\n"
        f"[cyan]Max Parallel Requests:[/cyan] {settings['max_parallel_requests']}\n"
        f"[cyan]Require Confirmation:[/cyan] {settings['require_confirmation']}",
        title="System Settings"
    ))

@click.group()
def cli():
    """ConsultAI Dashboard - View and manage system settings"""
    pass

@cli.command()
@click.option('--tier', type=click.Choice(['economy', 'balanced', 'performance']), default='balanced')
def models(tier: str):
    """Display model information and recommendations"""
    model_manager = ModelManager(ModelTier(tier))
    display_model_info(model_manager)
    console.print("\n")
    display_task_models(model_manager)

@cli.command()
def cases():
    """Display available case studies"""
    dashboard = DashboardConfig()
    display_case_studies(dashboard)

@cli.command()
def roles():
    """Display available roles"""
    dashboard = DashboardConfig()
    display_roles(dashboard)

@cli.command()
@click.option('--tier', type=click.Choice(['economy', 'balanced', 'performance']), default='balanced')
def settings(tier: str):
    """Display current system settings"""
    dashboard = DashboardConfig(model_tier=ModelTier(tier))
    display_system_settings(dashboard)

@cli.command()
def all():
    """Display all dashboard information"""
    dashboard = DashboardConfig()
    model_manager = ModelManager(dashboard.model_tier)
    
    console.print("\n[bold cyan]System Settings[/bold cyan]")
    display_system_settings(dashboard)
    
    console.print("\n[bold cyan]Models[/bold cyan]")
    display_model_info(model_manager)
    console.print("\n")
    display_task_models(model_manager)
    
    console.print("\n[bold cyan]Case Studies[/bold cyan]")
    display_case_studies(dashboard)
    
    console.print("\n[bold cyan]Roles[/bold cyan]")
    display_roles(dashboard)

if __name__ == '__main__':
    cli() 