from typing import List, Dict, Callable, ContextManager
from smolagents import CodeAgent, ChatMessage, LogLevel
from prompt import Prompt

ADDITIONAL_AUTHORIZED_IMPORTS = [
    "pandas",
    "matplotlib.pyplot",
    "matplotlib.colors",
]


class Agent:
    def __init__(
        self,
        model: Callable[[List[Dict[str, str]]], ChatMessage],
        context: ContextManager[None],
        verbosity_level: LogLevel = LogLevel.INFO,
    ):
        self.agent = CodeAgent(
            model=model,
            tools=[],
            verbosity_level=verbosity_level,
            additional_authorized_imports=ADDITIONAL_AUTHORIZED_IMPORTS,
        )

        self.context = context

    def run(self, task: str, files: List[str] = []):
        """Execute the AI agent on the given task with the given source files."""
        prompt = str(Prompt(task, files))

        # the agent run within an execution context monitoring file writes and with matplotlib in server mode.
        with self.context:
            self.agent.run(prompt)

    def more(self, prompt: str, files: List[str] = []):
        """Keep executing the agent with a new prompt."""
        with self.context:
            self.agent.run(prompt, reset=False)
