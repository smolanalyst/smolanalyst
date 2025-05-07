#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmolAnalyst CLI - Command line interface for AI-powered data analysis.

This module provides a command-line interface for managing and running
the SmolAnalyst data analysis tool. It handles configuration, Podman
container management, and task execution.
"""

import os
import json
import shutil
import tempfile
import datetime
import subprocess
from pathlib import Path
from typing import TypedDict, List, Optional

# Third-party imports
import typer
import platformdirs
from rich.console import Console

# Internal imports
from smolanalyst.constants import (
    APP_NAME,
    ENV_NAME,
    ENV_VERSION,
    WORK_DIR,
    SOURCE_FILES_DIR,
)

# Application constants
IMAGE_NAME = f"{ENV_NAME}:{ENV_VERSION}"

# Configuration paths
CONFIG_DIR = Path(platformdirs.user_config_dir(APP_NAME))
CONFIG_FILE = CONFIG_DIR / "config.json"

# Rich console for prettier output
console = Console()

# Create typer app and subcommands
app = typer.Typer(help="AI agent for data analysis")
conf_app = typer.Typer(help="Configuration management")
app.add_typer(conf_app, name="conf")


class ModelConfig(TypedDict):
    """Type definition for model configuration data."""

    type: str  # Model type (hfapi|litellm)
    model_id: str  # Model identifier
    api_key: str  # API key for authentication
    api_base: str  # Base URL for API requests


def read_config() -> ModelConfig:
    """
    Read and parse the configuration file.

    Returns:
        ModelConfig: The loaded configuration.

    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
        json.JSONDecodeError: If the configuration file is invalid JSON.
    """
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Configuration file not found ({CONFIG_FILE})")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return ModelConfig(
        type=config["type"],
        model_id=config["model_id"],
        api_key=config["api_key"],
        api_base=config["api_base"],
    )


@app.command("init")
@app.command("configure")
def configure() -> None:
    """Initialize or update configuration interactively."""
    conf_set()


@conf_app.command("set")
def conf_set() -> None:
    """Set configuration values interactively and save to config file."""
    console.print(f"Writing {APP_NAME} configuration file: {CONFIG_FILE}")

    # Collect configuration values from user
    config = {}
    config["type"] = typer.prompt("Model type (hfapi|litellm)")
    config["model_id"] = typer.prompt("Model ID")
    config["api_key"] = typer.prompt("Model API key", hide_input=True)
    config["api_base"] = typer.prompt("Model API base URL")

    # Create config directory if it doesn't exist
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Write configuration to file
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
        console.print("\n[green]Configuration file saved successfully.[/green]")
    except Exception as e:
        console.print(f"[red]Error saving configuration file: {e}[/red]")


@conf_app.command("show")
def conf_show() -> None:
    """Display the current configuration."""
    console.print(f"Reading {APP_NAME} configuration file: {CONFIG_FILE}")

    try:
        config = read_config()
        # Hide API key in display
        display_config = {**config}
        if display_config.get("api_key"):
            display_config["api_key"] = "********"
        console.print_json(json.dumps(display_config))
    except FileNotFoundError:
        console.print("[yellow]Configuration file not found.[/yellow]")
    except json.JSONDecodeError:
        console.print("[red]Invalid configuration file format.[/red]")
    except Exception as e:
        console.print(f"[red]Error reading configuration file: {e}[/red]")


@conf_app.command("delete")
def conf_delete() -> None:
    """Delete the configuration file."""
    console.print(f"Deleting {APP_NAME} configuration file: {CONFIG_FILE}")

    try:
        os.remove(CONFIG_FILE)
        console.print("[green]Configuration file deleted successfully.[/green]")
    except FileNotFoundError:
        console.print("[yellow]Configuration file not found.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error deleting configuration file: {e}[/red]")


@app.command("build")
def build() -> None:
    """Build the container image using Podman."""
    # Get the directory containing this script
    build_path = Path(__file__).parent.resolve()

    console.print(f"Building container image: {IMAGE_NAME}")
    try:
        subprocess.run(["podman", "build", "-t", IMAGE_NAME, build_path], check=True)
        console.print("[green]Container image built successfully.[/green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error building container image: {e}[/red]")
    except FileNotFoundError:
        console.print(
            "[red]Error: Podman not found. Please install Podman to build the container.[/red]"
        )


@app.command("run")
def run(
    files: List[Path] = typer.Argument(None, help="One or more data files to analyze"),
    task: Optional[str] = typer.Option(
        None, "--task", "-t", help="Task description to perform"
    ),
) -> None:
    """Run a data analysis task in a container."""
    # Read the configuration file
    try:
        config = read_config()
    except FileNotFoundError:
        console.print(
            "[yellow]Configuration file not found. Please run 'configure' first.[/yellow]"
        )
        return
    except json.JSONDecodeError:
        console.print(
            "[red]Invalid configuration file format. Please run 'configure' again.[/red]"
        )
        return
    except Exception as e:
        console.print(f"[red]Error reading configuration file: {e}[/red]")
        return

    # Prepare volume mappings for data files
    volumes = []
    try:
        for file_path in files:
            if file_path.exists():
                absolute_path = str(file_path.absolute())
                file_dest_path = f"{SOURCE_FILES_DIR}/{file_path.name}"
                volumes.append((absolute_path, file_dest_path))
            else:
                console.print(
                    f"[yellow]Warning: File {file_path} not found. Skipping.[/yellow]"
                )
    except Exception as e:
        console.print(f"[red]Error processing input files: {e}[/red]")
        return

    if not volumes and files:
        console.print("[yellow]No valid input files found.[/yellow]")
        return

    # Get the task from arguments or prompt user
    task_desc = task
    if not task_desc:
        task_desc = typer.prompt("What analysis would you like to perform?")

    # Run the command with a temporary directory for outputs
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Build the podman command
            cmd = [
                "podman",
                "run",
                "-it",
                "--rm",
                f"-e MODEL_TYPE={config['type']}",
                f"-e MODEL_ID={config['model_id']}",
                f"-e MODEL_API_KEY={config['api_key']}",
                f"-e MODEL_API_BASE={config['api_base']}",
                "-v",
                f"{tmp_dir}:{WORK_DIR}:rw",
            ]

            # Add volume mappings for data files
            for src, dest in volumes:
                cmd.append("-v")
                cmd.append(f"{src}:{dest}:ro")

            # Add image name and task
            cmd.append(IMAGE_NAME)
            cmd.append(task_desc)

            # Run the container
            console.print("[blue]Starting analysis...[/blue]")
            subprocess.run(cmd)

            # Copy generated files to current directory
            copy_files_to_cwd(tmp_dir)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running container: {e}[/red]")
    except FileNotFoundError:
        console.print(
            "[red]Error: Podman not found. Please install Podman to run the container.[/red]"
        )
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")


def copy_files_to_cwd(source_dir: str) -> None:
    """
    Copy all files from the source directory to the current working directory,
    preserving the directory structure. Avoids overwriting existing files by
    appending a timestamp to the filename.

    Args:
        source_dir (str): Path to the source directory
    """
    source_path = Path(source_dir)
    cwd = Path.cwd()

    # Walk through all files recursively with pathlib
    for source_file in source_path.glob("**/*"):
        # Skip directories, only process files
        if not source_file.is_file():
            continue

        # Get relative path from source directory
        rel_path = source_file.relative_to(source_path)
        dest_file = cwd / rel_path

        # Create parent directories if needed
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # If file exists, append timestamp to the filename
        if dest_file.exists():
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_file = dest_file.with_name(
                f"{dest_file.stem}_{timestamp}{dest_file.suffix}"
            )

        # Copy the file
        shutil.copy2(source_file, dest_file)
        print(f"Created: {dest_file.relative_to(cwd)}")


def main() -> None:
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
