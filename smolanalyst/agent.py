from pathlib import Path
from typing import List, Dict, Callable
from smolagents import CodeAgent, ChatMessage, LogLevel
from prompt import Prompt
from execution_context import ExecutionContext


class Agent:
    def __init__(
        self,
        model: Callable[[List[Dict[str, str]]], ChatMessage],
        verbosity_level: LogLevel = LogLevel.INFO,
    ):
        self.agent = CodeAgent(
            model=model,
            tools=[],
            verbosity_level=verbosity_level,
            additional_authorized_imports=[
                "pandas",
                "matplotlib.pyplot",
                "matplotlib.colors",
            ],
        )

    def validate_existing_files(self, files: List[str]) -> List[str]:
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

    def run(self, task: str, files: List[str] = []):
        """Execute the AI agent on the given task with the given source files."""
        files = self.validate_existing_files(files)

        prompt = str(Prompt(task, files))

        # the agent run within an execution context monitoring file writes and with matplotlib in server mode.
        with ExecutionContext.cwd().secure_context():
            self.agent.run(prompt)
