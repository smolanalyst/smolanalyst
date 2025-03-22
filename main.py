import argparse
from pathlib import Path
from typing import Optional, List
from smolagents import CodeAgent, HfApiModel, LogLevel, Tool


def parse_arguments():
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    parser.add_argument("files", nargs="+", help="One or more tabular data files.")
    parser.add_argument("-p", "--prompt", help="Analysis prompt.")
    parser.add_argument("-v", "--verbose", action="store_true", default=False)

    return parser.parse_args()


def validate_existing_files(file_paths: List[str]) -> List[Path]:
    """Return a list of existing files. TODO: accept glob patterns."""
    files = []

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Error: File not found: {file_path}")
        if not path.is_file():
            raise FileNotFoundError(f"Error: Not a file: {file_path}")
        files.append(path)

    if len(files) == 0:
        raise ValueError("Error: No files provided.")

    return files


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


class GetAvailableDataFileList(Tool):
    name = "get_avaliabe_data_file_list"
    description = "Return the list of available data files."
    inputs = {}
    output_type = "array"

    def __init__(self, files: List[Path]):
        self.files = files
        super().__init__()

    # TODO: maybe list the sheets from excel files?
    def forward(self):
        return self.files


def main(
    files: List[Path],
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
        tools=[GetAvailableDataFileList(files)],
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
