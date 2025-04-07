from typing import List
from string import Template

EXTRA_INSTRUCTIONS = """
Task: $task

### Guidelines for Data Analysis:
- **No Internet Access:** You cannot fetch external data. Work only with the provided files.
- **Inspect Data:** You can preview a few rows before proceeding with the analysis.
- **Multiple Sheets:** If dealing with Excel files, check for multiple sheets before assuming the structure.
- **File Saving:**
    - Do not save any files unless explicitly instructed.
    - If file writing fails because it alread exists, you are allowed to append a timestamp to the filename and retry.
    - If file writing is not allowed, clearly state it and stop processing.
- **Chart Handling:** Matplotlib runs in headless mode so displaying charts is useless.
- **Missing Data:** If no suitable data is available for the task, clearly state it and stop processing.
""".strip()

EXTRA_INSTRUCTIONS_WITH_SOURCE_FILES = f"""
{EXTRA_INSTRUCTIONS}

### Available Source Files:
$files
""".strip()


class Prompt:
    def __init__(self, task: str, files: List[str] = []):
        self.task = task
        self.files = files

    def __str__(self):
        if len(self.files) == 0:
            return Template(EXTRA_INSTRUCTIONS).substitute(task=self.task)

        return Template(EXTRA_INSTRUCTIONS_WITH_SOURCE_FILES).substitute(
            task=self.task, files="\n".join("- " + file for file in self.files)
        )
