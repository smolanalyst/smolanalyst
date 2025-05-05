from string import Template

EXTRA_INSTRUCTIONS = """
Task: $task

---

## Guidelines for Data Analysis

### Data Source Limitations
- **No Internet Access**: Work exclusively with the provided source files
- **Source File Path**: The provided source file path is absolute

### Initial Steps
- **Inspect the Data First**: Preview a few rows to understand structure and contents
- **Excel Files**: Always check for multiple sheets; never assume structure based on first sheet alone

### Technical Considerations
- **Chart Handling**: Matplotlib runs in headless mode—save charts instead of displaying them
- **Directory Creation**: You are permitted to create directories as needed

### Error Handling
- **Missing/Inadequate Data**: Clearly state the issue and terminate analysis if suitable data cannot be found
""".strip()

EXTRA_INSTRUCTIONS_WITH_SOURCE_FILES = f"""
{EXTRA_INSTRUCTIONS}

### Available Source Files:
$files
""".strip()


class SmolanalystPrompt:
    def __init__(self, task: str, files: list[str] = []):
        self.task = task
        self.files = files

    def __str__(self):
        if len(self.files) == 0:
            return Template(EXTRA_INSTRUCTIONS).substitute(task=self.task)

        return Template(EXTRA_INSTRUCTIONS_WITH_SOURCE_FILES).substitute(
            task=self.task, files="\n".join("- " + file for file in self.files)
        )
