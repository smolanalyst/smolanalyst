#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SmolAnalyst Runner - Main execution module for AI-powered data analysis.

This module handles the core functionality of running the AI analysis agent,
connecting to the LLM backend, and managing file interactions. It serves as
the bridge between the CLI interface and the actual analysis execution.
"""

import os
import sys
import stat
from typing import List, Optional, Union
from pathlib import Path

# Third-party imports
from smolagents import CodeAgent, LogLevel, HfApiModel, LiteLLMModel

# Internal imports
# The script runs inside the image so it must not be prepended with the package name
from prompt import SmolanalystPrompt
from filesystem import set_full_permissions
from constants import WORK_DIR, SOURCE_FILES_DIR, ADDITIONAL_AUTHORIZED_IMPORTS

# Environment variables for model configuration
MODEL_ID = os.getenv("MODEL_ID")
MODEL_TYPE = os.getenv("MODEL_TYPE")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
MODEL_API_BASE = os.getenv("MODEL_API_BASE")

# Type alias for model types
ModelType = Union[HfApiModel, LiteLLMModel]


def _build_model() -> Optional[ModelType]:
    """
    Internal function to create an appropriate model instance based on environment variables.

    Returns:
        Optional[ModelType]: The initialized model instance or None if configuration is invalid.
    """
    if not MODEL_TYPE or not MODEL_ID:
        return None

    if MODEL_TYPE == "hfapi":
        return HfApiModel(model_id=MODEL_ID, token=MODEL_API_KEY)
    elif MODEL_TYPE == "litellm":
        return LiteLLMModel(
            model_id=MODEL_ID,
            api_key=MODEL_API_KEY,
            api_base=MODEL_API_BASE,
        )
    return None


def build_model() -> ModelType:
    """
    Create and validate a model instance based on environment configuration.

    Returns:
        ModelType: The initialized model instance.

    Raises:
        ValueError: If the model cannot be initialized with the given configuration.
    """
    model = _build_model()

    if model:
        return model

    # Format a helpful error message with the current configuration
    config = "\n"
    config += f"- MODEL_TYPE: {MODEL_TYPE or 'not defined'}\n"
    config += f"- MODEL_ID: {MODEL_ID or 'not defined'}\n"
    config += f"- MODEL_API_KEY: {MODEL_API_KEY or 'not defined'}\n"
    config += f"- MODEL_API_BASE: {MODEL_API_BASE or 'not defined'}\n"

    raise ValueError(f"Unable to build a model - check environment variables:{config}")


def list_source_files(directory: str) -> List[str]:
    """
    List all files in a directory and its subdirectories.

    Args:
        directory (str): Path to the directory to scan.

    Returns:
        List[str]: List of absolute paths to all files found.
    """
    file_list = []
    dir_path = Path(directory)

    if not dir_path.exists():
        return []

    try:
        for path in dir_path.rglob("*"):
            if path.is_file():
                file_list.append(str(path.absolute()))
    except Exception:
        return []

    return file_list


def run(task: str) -> None:
    """
    Run a data analysis task using the AI agent.

    Args:
        task (str): Description of the analysis task to perform.
    """
    # Set matplotlib backend to Agg for headless environments
    import matplotlib

    matplotlib.use("Agg")

    # Build model according to environment variables
    model = build_model()

    # List files from the source directory
    files = list_source_files(SOURCE_FILES_DIR)

    # Create code agent with appropriate permissions
    agent = CodeAgent(
        model=model,
        tools=[],  # No additional tools configured
        additional_authorized_imports=ADDITIONAL_AUTHORIZED_IMPORTS,
        verbosity_level=LogLevel.DEBUG,
    )

    # Create analysis prompt
    prompt = SmolanalystPrompt(task, files)

    # Run the initial task
    agent.run(str(prompt))

    # Set permissions on output files
    set_full_permissions(WORK_DIR)

    # Handle user followup queries
    while True:
        more = input("\nIs this ok? (Enter followup question or 'q' to quit)\n> ")

        if more.lower() == "q":
            break

        agent.run(more, reset=False)

        # Set permissions after each run
        set_full_permissions(WORK_DIR)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runner.py 'your task here'")
        sys.exit(1)

    task = sys.argv[1]
    run(task)
