import os
import json
import argparse
import platformdirs
from typing import List
from pathlib import Path
from smolagents import LogLevel
from agent import Agent
from model import ModelType, ModelConfig, model_factory
from context import ExecutionContext

APP_NAME = "smolanalyst"
CONFIG_DIR = platformdirs.user_config_dir(APP_NAME)
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    subparsers1 = parser.add_subparsers()

    # configuration commands.
    subparsers1.add_parser("init").set_defaults(func=conf_set)
    subparsers1.add_parser("configure").set_defaults(func=conf_set)

    conf = subparsers1.add_parser("conf")
    subparsers2 = conf.add_subparsers()
    subparsers2.add_parser("set").set_defaults(func=conf_set)
    subparsers2.add_parser("show").set_defaults(func=conf_show)
    subparsers2.add_parser("delete").set_defaults(func=conf_delete)

    # run command.
    run_agent = subparsers1.add_parser("run")
    run_agent.add_argument("files", nargs="*", help="One or more data files.")
    run_agent.add_argument("-t", "--task", help="Task to perform.")
    run_agent.add_argument("-v", "--verbose", action="store_true", default=False)
    run_agent.set_defaults(func=run)

    return parser.parse_args()


def read_config() -> ModelConfig:
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("Configuration file not found ({CONFIG_FILE})")

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    return ModelConfig(
        type=ModelType[str(config["type"]).upper()],
        model_id=config["model_id"],
        api_key=config["api_key"],
        api_base=config["api_base"],
    )


def conf_set(_):
    print(f"Writting {APP_NAME} configuration file: {CONFIG_FILE}")

    config = {}
    config["type"] = input("model type (hfapi|litellm)\n> ")
    config["model_id"] = input("model id:\n> ")
    config["api_key"] = input("model api key:\n> ")
    config["api_base"] = input("model api base:\n> ")

    os.makedirs(CONFIG_DIR, exist_ok=True)

    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=4)
            print(f"\nConfiguration file saved.")
    except Exception as e:
        print(f"Error saving configuration file: {e}")


def conf_show(_):
    print(f"Reading {APP_NAME} configuration file: {CONFIG_FILE}")

    try:
        config = read_config()
        print(json.dumps(config, indent=4))
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"Error reading configuration file: {e}")


def conf_delete(_):
    print(f"Deleting {APP_NAME} configuration file: {CONFIG_FILE}")

    try:
        os.remove(CONFIG_FILE)
        print(f"Configuration file deleted.")
    except FileNotFoundError:
        print("Configuration file not found.")
    except Exception as e:
        print(f"Error deleting configuration file: {e}")


def validate_existing_files(files: List[str]) -> List[str]:
    """Return a list of existing files. TODO: accept glob patterns."""
    valid_files = []

    for file in files:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file}")
        if not path.is_file():
            raise FileNotFoundError(f"Not a file: {file}")
        valid_files.append(file)

    return valid_files


def run(args):
    # read the configuration file.
    try:
        config = read_config()
    except FileNotFoundError:
        print("Configuration file not found. Please run 'configure' first.")
    except Exception as e:
        print(f"Error reading configuration file: {e}")

    # create a model from the configuration.
    model = model_factory(config)

    # validate the files exists.
    files = validate_existing_files(args.files)

    # prompt user if no task given.
    task = args.task

    if not task:
        task = input("What analysis would you like to perform?\n> ")

    # execution context is in cwd.
    context = ExecutionContext.cwd()

    # format the verbosity level.
    verbosity_level = LogLevel.DEBUG if args.verbose else LogLevel.INFO

    # create the agent.
    agent = Agent(model, context, verbosity_level)

    # run the agent.
    agent.run(task, files)

    # loop until the user ends chatting with the agent.
    while True:
        # prompt user for more.
        more = input("Is this ok? (q to quit)\n> ")

        if more.lower() == "q":
            break

        # run the agent with the new prompt.
        agent.more(more)


if __name__ == "__main__":
    args = parse_arguments()

    args.func(args)
