import argparse
from pathlib import Path
from typing import Optional, List
from smolagents import CodeAgent, HfApiModel, LogLevel


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


def get_augmented_prompt(files: List[Path], prompt: str) -> str:
    return f"""
## You are a machine learning specialist focused on data analysis.

You have access to the following files:
{"\n".join(["- " + str(file) for file in files])}

### Instructions:
- Always check all sheets of Excel files before selecting relevant data.
- Always inspect the first few rows of each relevant table to understand its structure.
- All plots and charts must be **saved to a file** and **not displayed**.

### Task:
{prompt}"""


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

    prompt = get_augmented_prompt(files, prompt)

    agent = CodeAgent(
        model=model,
        tools=[],
        add_base_tools=True,
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
