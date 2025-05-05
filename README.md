# SmolAnalyst

SmolAnalyst is an AI agent that analyzes data files by generating and executing Python snippets. Built on [Hugging Face](https://huggingface.co/)'s [Smolagent](https://github.com/huggingface/smolagents), it primarily runs through a CLI tool but can be integrated into other environments.

## What is SmolAnalyst?

SmolAnalyst is a tool that allows you to analyze data using natural language instructions. It uses Hugging Face's Smolagent to generate Python code that processes your data files within a secure containerized environment. The tool handles the execution environment, file management, and security aspects so you can focus on your analysis tasks.

## Installation

SmolAnalyst can be installed globally from PyPI using [uv](https://github.com/astral-sh/uv), a lightning-fast Python package manager:

```bash
# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install SmolAnalyst globally
uv tool install smolanalyst
```

This will install SmolAnalyst in an isolated environment and make the `smolanalyst` command available globally in your terminal.

If you prefer using traditional pip:

```bash
pip install smolanalyst
```

## Analysis Workflow

SmolAnalyst follows a secure and efficient workflow for data analysis:

1. **Configure**: Set up your LLM backend (only needed once)

   ```bash
   smolanalyst configure
   ```

2. **Build**: Build the container image with Podman (required once after installing a new version)

   ```bash
   smolanalyst build
   ```

3. **Run**: Execute an analysis task with your data files
   ```bash
   smolanalyst run [files] -t "your analysis task"
   ```

### How the Workflow Works

When you run an analysis with SmolAnalyst, the following happens:

1. Your source files are mounted as read-only in a Podman container
2. A temporary directory is mounted as writable for output files
3. The container runs a Smolagent session with special instructions about your files
4. The AI agent generates and executes Python code to analyze your data
5. Output files are written to the temporary directory
6. When the analysis completes, files from the temporary directory are copied to your current working directory
7. If a file with the same name already exists, a timestamp is added to the filename to prevent overwriting

This containerized approach ensures that:

- Your original data remains untouched
- The AI agent can only access the files you explicitly provide
- The execution environment is isolated from your system for security
- All generated files are properly managed and accessible after analysis

## CLI Configuration

To configure SmolAnalyst, run the following command:

```bash
smolanalyst configure
```

This command will prompt you to provide the following:

- `model type`: The backend used to access the model. Use `hfapi` for [Hugging Face](https://huggingface.co/) Inference API or `litellm` for [LiteLLM](https://www.litellm.ai/).
- `model id`: The identifier of the model you want to use.
- `model api key`: Your API key for the selected provider.
- `model base`: The base URL of the model API (used for local deployments like [Ollama](https://ollama.com/)).

After completing the prompts, a `config.json` file will be saved to your home directory with the configuration details.

### Example Configurations

#### Qwen2.5-Coder-32B-Instruct via Hugging Face

A high-performance model using the [Hugging Face](https://huggingface.co/) Inference API:

```json
{
  "type": "hfapi",
  "model_id": "Qwen/Qwen2.5-Coder-32B-Instruct",
  "api_key": "secret",
  "api_base": ""
}
```

#### Gemini 2.0 Flash Lite via LiteLLM

A lightweight model with a generous free tier:

```json
{
  "type": "litellm",
  "model_id": "gemini/gemini-2.0-flash-lite",
  "api_key": "secret",
  "api_base": ""
}
```

#### Local Qwen2.5 via Ollama

Run a model locally using [Ollama](https://ollama.com/):

```json
{
  "type": "litellm",
  "model_id": "ollama/qwen2.5-coder:32b",
  "api_key": "",
  "api_base": "http://127.0.0.1:11434"
}
```

## Running an Analysis

To start an analysis, run the following command:

```bash
smolanalyst run [files] -t "your task description"
```

- `[files]` is a list of zero or more file paths. These files will be explicitly referenced in SmolAnalyst's prompt.
- Use the `-t` option to specify a task directly. If omitted, SmolAnalyst will prompt you to describe the task.

### Example Usage

Here's a practical example of using SmolAnalyst to analyze sales data:

```bash
smolanalyst run data/sales.xlsx -t "create a list of number of boxes shipped per salesman and save it in box_shipped.xlsx"
```

This command will:

1. Mount the sales.xlsx file in the container
2. Ask the AI agent to analyze the data and create a list of boxes shipped per salesman
3. Generate and save the results in a file called box_shipped.xlsx
4. Copy the output file to your current directory

**Execution Environment Restrictions:**

- SmolAnalyst currently supports importing pandas and matplotlib libraries
- It can write files using these libraries, but only within the container's writable directory
- Files are automatically copied to your current working directory after analysis

## Technical Details

SmolAnalyst uses Podman for containerization instead of Docker. This provides several advantages:

- Rootless containers for enhanced security
- Reduced attack surface
- Compatible with systems where Docker isn't available or preferred

The container includes a Python environment with essential data analysis libraries. When you run an analysis, your files are mounted in this container, and the AI agent generates and executes Python code to process your data.

## Roadmap

We're actively working on improving SmolAnalyst. Here are our planned enhancements:

### Near-term Improvements

- Expand the analysis capabilities by adding more data science packages
- Implement real-time file monitoring to provide feedback during analysis

### User Experience

- Enhance the configuration management system for multiple LLM profiles
- Improve the CLI interface with a more polished user experience

### Architecture Evolution

- Develop a server-based solution with a web interface for easier interaction
- Create a flexible system for connecting to various data sources (databases, cloud storage)
- Refine the container and runner architecture for better maintainability

## Contributing

We're looking for people to test SmolAnalyst and contribute to its development! If you're interested in helping out, here are some ways to contribute:

1. Try SmolAnalyst with your own data and report any issues
2. Suggest new features or improvements
3. Help with documentation
4. Contribute code for new features or bug fixes

## License

SmolAnalyst is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.

## Acknowledgements

SmolAnalyst is built on top of several amazing open-source projects:

- [Hugging Face Smolagents](https://github.com/huggingface/smolagents) for the AI agent framework
- [Podman](https://podman.io/) for containerization
- [Pandas](https://pandas.pydata.org/) and [Matplotlib](https://matplotlib.org/) for data analysis and visualization

We're grateful to the maintainers of these projects for their incredible work.
