from typing import List
from string import Template

EXTRA_INSTRUCTIONS = """
Task: $task

---

### Guidelines for Data Analysis

- **No Internet Access:**  
  Do **not** attempt to download or fetch external resources. You must work **only** with the provided local files.

- **Inspect the Data First:**  
  Before starting any analysis, preview a few rows to understand the structure and contents.

- **Excel Files – Multiple Sheets:**  
  Always check for multiple sheets in Excel files. Never assume the structure is based on the first sheet alone.

- **File Saving Rules:**  
  - Saving files is allowed **only** via authorized import methods.  
  - If file writing is **not allowed**, clearly state the limitation and stop processing.  
  - If saving to an **existing filename**, append a timestamp to create a new filename, retry, and notify about the change.

- **Chart Handling – Headless Mode:**  
  Matplotlib is running in headless mode, so do **not** attempt to display charts. Generate and save them instead if required.

- **Missing or Inadequate Data:**  
  If no suitable data is found for the task, clearly state the issue and stop the analysis.
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
