import os
import argparse
from typing import Optional
from smolagents import LogLevel
from agent import Agent
from model import ModelFactory


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    parser.add_argument("files", nargs="*", help="One or more data files.")
    parser.add_argument("-t", "--task", help="Task to perform.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False)

    return parser.parse_args()


def prompt_task(task: Optional[str] = None) -> str:
    """Get task from argument or prompt user."""
    if task:
        return task
    return input("What analysis would you like to perform?\n> ")


if __name__ == "__main__":
    args = parse_arguments()

    task = prompt_task(args.task)

    factory = ModelFactory(
        os.environ.get("SMOLANALYST_MODEL_TYPE", "HFAPI"),
        os.environ.get("SMOLANALYST_MODEL_ID"),
        os.environ.get("SMOLANALYST_MODEL_API_KEY"),
        os.environ.get("SMOLANALYST_MODEL_API_BASE"),
    )

    verbosity_level = LogLevel.DEBUG if args.verbose else LogLevel.INFO

    agent = Agent(factory(), verbosity_level)

    agent.run(task, args.files)
