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
import argparse
import tempfile
import datetime
import subprocess
from pathlib import Path
from typing import TypedDict

# Third-party imports
import platformdirs

# Internal imports
from smolanalyst.config import WORK_DIR, SOURCE_FILES_DIR

# Application constants
APP_NAME = "smolanalyst"
ENV_NAME = "smolanalyst"
ENV_VERSION = "0.1.0"
IMAGE_NAME = f"{ENV_NAME}:{ENV_VERSION}"

# Configuration paths
CONFIG_DIR = platformdirs.user_config_dir(APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


class ModelConfig(TypedDict):
    """Type definition for model configuration data."""

    type: str  # Model type (hfapi|litellm)
    model_id: str  # Model identifier
    api_key: str  # API key for authentication
    api_base: str  # Base URL for API requests


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    # Create subparsers for main commands
    subparsers1 = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers1.required = True  # Require a command to be specified

    # Configuration commands
    subparsers1.add_parser("init", help="Initialize configuration").set_defaults(
        func=conf_set
    )
    subparsers1.add_parser("configure", help="Configure the application").set_defaults(
        func=conf_set
    )

    # Configuration subcommands
    conf = subparsers1.add_parser("conf", help="Configuration management")
    subparsers2 = conf.add_subparsers(
        dest="subcommand", help="Configuration subcommand"
    )
    subparsers2.required = True  # Require a subcommand to be specified

    subparsers2.add_parser("set", help="Set configuration values").set_defaults(
        func=conf_set
    )
    subparsers2.add_parser("show", help="Show current configuration").set_defaults(
        func=conf_show
    )
    subparsers2.add_parser("delete", help="Delete configuration").set_defaults(
        func=conf_delete
    )

    # Build command
    build_parser = subparsers1.add_parser("build", help="Build the container image")
    build_parser.set_defaults(func=build)

    # Run command
    run_parser = subparsers1.add_parser("run", help="Run a data analysis task")
    run_parser.add_argument(
        "files", nargs="*", help="One or more data files to analyze"
    )
    run_parser.add_argument("-t", "--task", help="Task description to perform")
    run_parser.set_defaults(func=run)

    return parser.parse_args()


def read_config() -> ModelConfig:
    """
    Read and parse the configuration file.

    Returns:
        ModelConfig: The loaded configuration.

    Raises:
        FileNotFoundError: If the configuration file doesn't exist.
    """
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Configuration file not found ({CONFIG_FILE})")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return ModelConfig(
        type=config["type"],
        model_id=config["model_id"],
        api_key=config["api_key"],
        api_base=config["api_base"],
    )


def conf_set(_) -> None:
    """
    Set configuration values interactively and save to config file.

    Args:
        _: Unused arguments parameter.
    """
    print(f"Writing {APP_NAME} configuration file: {CONFIG_FILE}")

    # Collect configuration values from user
    config = {}
    config["type"] = input("Model type (hfapi|litellm)\n> ")
    config["model_id"] = input("Model ID:\n> ")
    config["api_key"] = input("Model API key:\n> ")
    config["api_base"] = input("Model API base URL:\n> ")

    # Create config directory if it doesn't exist
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Write configuration to file
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
            print(f"\nConfiguration file saved successfully.")
    except Exception as e:
        print(f"Error saving configuration file: {e}")


def conf_show(_) -> None:
    """
    Display the current configuration.

    Args:
        _: Unused arguments parameter.
    """
    print(f"Reading {APP_NAME} configuration file: {CONFIG_FILE}")

    try:
        config = read_config()
        print(json.dumps(config, indent=4))
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"Error reading configuration file: {e}")


def conf_delete(_) -> None:
    """
    Delete the configuration file.

    Args:
        _: Unused arguments parameter.
    """
    print(f"Deleting {APP_NAME} configuration file: {CONFIG_FILE}")

    try:
        os.remove(CONFIG_FILE)
        print(f"Configuration file deleted successfully.")
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"Error deleting configuration file: {e}")


def build(_) -> None:
    """
    Build the container image using Podman.

    Args:
        _: Unused arguments parameter.
    """
    # Get the directory containing this script
    build_path = Path(__file__).parent.resolve()

    print(f"Building container image: {IMAGE_NAME}")
    try:
        subprocess.run(["podman", "build", "-t", IMAGE_NAME, build_path], check=True)
        print("Container image built successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error building container image: {e}")
    except FileNotFoundError:
        print("Error: Podman not found. Please install Podman to build the container.")


def run(args) -> None:
    """
    Run a data analysis task in a container.

    Args:
        args: Command line arguments containing task and files.
    """
    # Read the configuration file
    try:
        config = read_config()
    except FileNotFoundError:
        print("Configuration file not found. Please run 'configure' first.")
        return
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return

    # Prepare volume mappings for data files
    volumes = []
    try:
        for file in set(args.files):
            if os.path.exists(file):
                absolute_path = os.path.abspath(file)
                file_dest_path = f"{SOURCE_FILES_DIR}/{os.path.basename(file)}"
                volumes.append((absolute_path, file_dest_path))
            else:
                print(f"Warning: File {file} not found. Skipping.")
    except Exception as e:
        print(f"Error processing input files: {e}")
        return

    if not volumes and args.files:
        print("No valid input files found.")
        return

    # Get the task from arguments or prompt user
    task = args.task
    if not task:
        task = input("What analysis would you like to perform?\n> ")

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
            cmd.append(task)

            # Run the container
            subprocess.run(cmd)

            # Copy generated files to current directory
            copy_files_to_cwd(tmp_dir)

    except subprocess.CalledProcessError as e:
        print(f"Error running container: {e}")
    except FileNotFoundError:
        print("Error: Podman not found. Please install Podman to run the container.")
    except Exception as e:
        print(f"Unexpected error: {e}")


def copy_files_to_cwd(source_dir: str) -> None:
    """
    Copy all files from the source directory to the current working directory,
    preserving the directory structure. Avoids overwriting existing files by
    appending a timestamp to the filename.

    Args:
        source_dir (str): Path to the source directory
    """
    cwd = os.getcwd()
    source_dir = os.path.abspath(source_dir)
    copied_files = False

    # Walk through the source directory
    for root, _, files in os.walk(source_dir):
        # Calculate the relative path from the source directory
        rel_path = os.path.relpath(root, source_dir)

        # Skip if no files in this directory
        if not files:
            continue

        # Create the same directory structure in the destination
        if rel_path != ".":
            dest_dir = os.path.join(cwd, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
        else:
            dest_dir = cwd

        # Copy each file
        for file in files:
            source_file = os.path.join(root, file)

            # Determine destination file path
            if rel_path == ".":
                dest_file = os.path.join(cwd, file)
            else:
                dest_file = os.path.join(cwd, rel_path, file)

            # If file exists, append timestamp to the filename
            if os.path.exists(dest_file):
                # Get current timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

                # Split the filename and extension
                filename, file_extension = os.path.splitext(file)

                # Create new filename with timestamp
                new_filename = f"{filename}_{timestamp}{file_extension}"

                # Update the destination file path
                if rel_path == ".":
                    dest_file = os.path.join(cwd, new_filename)
                else:
                    dest_file = os.path.join(cwd, rel_path, new_filename)

            # Copy the file
            shutil.copy2(source_file, dest_file)
            print(f"Created: {os.path.relpath(dest_file, cwd)}")
            copied_files = True

    if not copied_files:
        print("No output files were generated by the analysis.")


def main():
    try:
        args = parse_arguments()
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
