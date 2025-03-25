import os
from pathlib import Path
from typing import List, Optional
from smolagents import CodeAgent, HfApiModel, LiteLLMModel, LogLevel
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


def get_model(
    model_type: Optional[str] = None,
    model_id: Optional[str] = None,
    model_api_key: Optional[str] = None,
    model_api_base: Optional[str] = None,
):
    if not model_type:
        model_type = os.environ.get("SMOLANALYST_MODEL_TYPE", "hfapi")

    if not model_id:
        model_id = os.environ.get("SMOLANALYST_MODEL_ID")

    if not model_api_key:
        model_api_key = os.environ.get("SMOLANALYST_MODEL_API_KEY")

    if not model_api_base:
        model_api_base = os.environ.get("SMOLANALYST_MODEL_API_BASE")

    if model_type == "hfapi":
        return HfApiModel(model_id=model_id, token=model_api_key)
    elif model_type == "litellm":
        return LiteLLMModel(
            model_id=model_id, api_key=model_api_key, api_base=model_api_base
        )
    else:
        raise ValueError(f"Invalid model type: {model_type}")


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
    model_type: Optional[str] = None,
    model_id: Optional[str] = None,
    model_api_key: Optional[str] = None,
    model_api_base: Optional[str] = None,
):
    """Execute the AI agent on the given task with the given options."""
    files = validate_existing_files(files)
    verbosity_level = validate_verbosity_level(verbose)

    model = get_model(model_type, model_id, model_api_key, model_api_base)
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
