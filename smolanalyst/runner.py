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
from typing import List, Optional

# Internal imports
from config import SOURCE_FILES_DIR
from prompt import SmolanalystPrompt
from smolagents import CodeAgent, LogLevel, HfApiModel, LiteLLMModel

# Allowed imports for the agent's execution environment
ADDITIONAL_AUTHORIZED_IMPORTS = [
    "os",
    "posixpath",
    "numpy",
    "pandas",
    "matplotlib",
    "matplotlib.pyplot",
]

# Environment variables for model configuration
MODEL_ID = os.getenv("MODEL_ID")
MODEL_TYPE = os.getenv("MODEL_TYPE")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
MODEL_API_BASE = os.getenv("MODEL_API_BASE")


def _build_model() -> Optional[HfApiModel | LiteLLMModel]:
    """
    Internal function to create an appropriate model instance based on environment variables.

    Returns:
        HfApiModel or LiteLLMModel or None: The initialized model instance or None if configuration is invalid.
    """
    match MODEL_TYPE:
        case "hfapi":
            return HfApiModel(model_id=MODEL_ID, token=MODEL_API_KEY)
        case "litellm":
            return LiteLLMModel(
                model_id=MODEL_ID,
                api_key=MODEL_API_KEY,
                api_base=MODEL_API_BASE,
            )
        case _:
            return None


def build_model() -> HfApiModel | LiteLLMModel:
    """
    Create and validate a model instance based on environment configuration.

    Returns:
        The initialized model instance.

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
    try:
        for root, _, files in os.walk(directory):
            for file in files:
                abspath = os.path.abspath(os.path.join(root, file))
                file_list.append(abspath)
    except FileNotFoundError:
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

    # Handle user followup queries
    while True:
        more = input("\nIs this ok? (Enter followup question or 'q' to quit)\n> ")

        if more.lower() == "q":
            break

        agent.run(more, reset=False)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runner.py 'your task here'")
        sys.exit(1)

    task = sys.argv[1]
    run(task)
