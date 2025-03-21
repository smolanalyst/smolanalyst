import argparse
from pathlib import Path
from typing import Optional, List
from smolagents import CodeAgent, HfApiModel


def execute_agent(prompt: str, files: List[Path]):
    """Execute the AI agent with the given prompt and files."""
    model = HfApiModel()

    agent = CodeAgent(
        model=model,
        tools=[],
        add_base_tools=True,
        additional_authorized_imports=[
            "pandas",
            "matplotlib.pyplot",
            "matplotlib.colors",
        ],
    )

    augmented_prompt = f"""
## You are a machine learning specialist focused on data analysis.

You have access to the following files:
{"\n".join(["- " + str(file) for file in files])}

### Instructions:
- Always check all sheets of Excel files before selecting relevant data.
- Always inspect the first few rows of each relevant table to understand its structure.
- All plots and charts must be **saved to a file** and **not displayed**.

### Task:
{prompt}"""

    agent.run(augmented_prompt)


def validate_existing_files(file_paths: List[str]) -> List[Path]:
    """Return a list of existing files. TODO: accept glob patterns."""
    valid_files = []

    for file_path in file_paths:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Error: File not found: {file_path}")
        if not path.is_file():
            raise FileNotFoundError(f"Error: Not a file: {file_path}")
        valid_files.append(path)

    return valid_files


def validate_optional_prompt(prompt: Optional[str] = None) -> str:
    """Get analysis prompt from argument or prompt user."""
    if prompt:
        return prompt
    return input("What analysis would you like to perform?\n> ")


def main():
    parser = argparse.ArgumentParser(description="AI agent for data analysis.")

    parser.add_argument("files", nargs="+", help="One or more tabular data files.")

    parser.add_argument("-p", "--prompt", help="Analysis prompt.")

    args = parser.parse_args()

    files = validate_existing_files(args.files)
    prompt = validate_optional_prompt(args.prompt)

    execute_agent(prompt, files)


if __name__ == "__main__":
    main()
