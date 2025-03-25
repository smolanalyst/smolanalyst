import argparse
from typing import Optional
from agent import run


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    parser.add_argument("-t", "--task", help="Task to perform.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False)
    parser.add_argument("-mt", "--model_type", help="Type of model to use.")
    parser.add_argument("-mi", "--model_id", help="Model ID.")
    parser.add_argument("-mk", "--model_api_key", help="Model API key.")
    parser.add_argument("-mb", "--model_api_base", help="Model API base URL.")

    parser.add_argument("files", nargs="*", help="One or more data files.")

    return parser.parse_args()


def prompt_task(task: Optional[str] = None) -> str:
    """Get task from argument or prompt user."""
    if task:
        return task
    return input("What analysis would you like to perform?\n> ")


if __name__ == "__main__":
    args = parse_arguments()

    task = prompt_task(args.task)

    run(
        task,
        args.files,
        args.verbose,
        args.model_type,
        args.model_id,
        args.model_api_key,
        args.model_api_base,
    )
