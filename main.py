import sys
import argparse
import matplotlib
from pathlib import Path
from typing import Optional, List
from smolagents import CodeAgent, HfApiModel, LogLevel, Tool
from io_management import handle_io_event

sys.addaudithook(handle_io_event)

# Use non-GUI backend so plt.shot() doesn't interrupt the execution.
matplotlib.use("Agg")


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    parser.add_argument("files", nargs="+", help="One or more data files.")
    parser.add_argument("-p", "--prompt", help="Analysis prompt.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False)

    return parser.parse_args()


def validate_existing_files(files: List[str]) -> List[Path]:
    """Return a list of existing files. TODO: accept glob patterns."""
    valid_files = []

    for file in files:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file}")
        if not path.is_file():
            raise FileNotFoundError(f"Not a file: {file}")
        valid_files.append(file)

    if len(valid_files) == 0:
        raise ValueError("No valid file provided.")

    return valid_files


def validate_optional_prompt(prompt: Optional[str] = None) -> str:
    """Get analysis prompt from argument or prompt user."""
    if prompt:
        return prompt
    return input("What analysis would you like to perform?\n> ")


def validate_verbosity_level(verbose: bool) -> LogLevel:
    """Return the log level according to the verbosity flag."""
    return LogLevel.DEBUG if verbose else LogLevel.INFO


def get_model():
    # TODO: select model according to environment variables.
    return HfApiModel()


class GetSourceDataFiles(Tool):
    name = "get_source_data_files"
    description = "Return the source data files you must work on."
    inputs = {}
    output_type = "array"

    def __init__(self, files: List[str]):
        self.files = files
        super().__init__()

    # TODO: maybe list the sheets from excel files?
    def forward(self):
        return self.files


def main(
    files: List[str],
    prompt: Optional[str] = None,
    verbose: bool = False,
):
    """Execute the AI agent with the given files and prompt."""
    model = get_model()
    files = validate_existing_files(files)
    prompt = validate_optional_prompt(prompt)
    verbosity_level = validate_verbosity_level(verbose)

    agent = CodeAgent(
        model=model,
        tools=[GetSourceDataFiles(files)],
        verbosity_level=verbosity_level,
        additional_authorized_imports=[
            "pandas",
            "matplotlib.pyplot",
            "matplotlib.colors",
        ],
    )

    agent.run(prompt)


if __name__ == "__main__":
    args = parse_arguments()

    main(args.files, args.prompt, args.verbose)
