from pathlib import Path
from typing import List
from smolagents import CodeAgent, HfApiModel, LogLevel
from contexts import RestrictedWriteContext, MatplotlibServerContext


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


def validate_verbosity_level(verbose: bool) -> LogLevel:
    """Return the log level according to the verbosity flag."""
    return LogLevel.DEBUG if verbose else LogLevel.INFO


def get_model():
    # TODO: select model according to environment variables.
    return HfApiModel()


def get_prompt(task: str, files: List[str]) -> str:
    """Augment the task to get a more precise prompt"""

    pieces = []

    pieces.append(f"Task: {task}")

    pieces.append(
        f"""
### Guidelines for Data Analysis:  
- **No Internet Access:** You cannot fetch external data. Work only with the provided files.  
- **Inspect Data:** You can preview a few rows before proceeding with the analysis.  
- **Multiple Sheets:** If dealing with Excel files, check for multiple sheets before assuming the structure.  
- **File Saving:**  
  - Do not save any files unless explicitly instructed.  
  - If saving fails, append a timestamp to the filename and retry.  
- **Chart Handling:** Matplotlib runs in headless mode, so always save charts to files instead of displaying them.  
- **Missing Data:** If no suitable data is available for the task, clearly state it and stop processing.  
        """.strip()
    )

    if len(files) > 0:
        pieces.append(
            f"""
### Available Source Files:
{"\n".join([f"- {file}" for file in files])}
            """.strip()
        )

    return "\n\n".join(pieces)


def run(
    task: str,
    files: List[str],
    verbose: bool = False,
):
    """Execute the AI agent on the given task with the given options."""
    files = validate_existing_files(files)
    verbosity_level = validate_verbosity_level(verbose)

    model = get_model()
    prompt = get_prompt(task, files)

    agent = CodeAgent(
        model=model,
        tools=[],
        verbosity_level=verbosity_level,
        additional_authorized_imports=[
            "pandas",
            "matplotlib.pyplot",
            "matplotlib.colors",
        ],
    )

    # the agent run is within an audit hook preneting the agent from
    # writing files outside the cwd and from overwriting files in the cwd.
    # Also matplotlib is temporarily switched to server backen so plt.show()
    # does not interrupt the agent execution.
    with RestrictedWriteContext(), MatplotlibServerContext():
        agent.run(prompt)
