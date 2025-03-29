from typing import List, Dict, Callable
from smolagents import CodeAgent, ChatMessage, LogLevel
from prompt import Prompt
from execution_context import ExecutionContext

ADDITIONAL_AUTHORIZED_IMPORTS = [
    "pandas",
    "matplotlib.pyplot",
    "matplotlib.colors",
]


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
            additional_authorized_imports=ADDITIONAL_AUTHORIZED_IMPORTS,
        )

    def run(self, task: str, files: List[str] = []):
        """Execute the AI agent on the given task with the given source files."""
        prompt = str(Prompt(task, files))

        # the agent run within an execution context monitoring file writes and with matplotlib in server mode.
        with ExecutionContext.cwd().secure_context():
            self.agent.run(prompt)
