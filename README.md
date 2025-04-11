# Smolanalyst

Smolanalyst is an AI agent that analyzes data files by generating and executing Python snippets. Built on [Hugging Face](https://huggingface.co/)'s [Smolagent](https://github.com/huggingface/smolagents), it primarily runs through a CLI tool but can be integrated into other environments.

## CLI Configuration

To configure Smolanalyst, run the following command:

```
python smolanalyst/cli.py configure
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

```
python smolanalyst/cli.py run [files]
```

- `[files]` is a list of zero or more file paths. These files will be explicitly referenced in Smolanalyst's prompt.
- Use the `-t` option to specify a task directly. If omitted, Smolanalyst will prompt you to describe the task.
- Add `-v` to enable verbose output, which includes the model's internal reasoning (thoughts).

**Execution Environment Restrictions:**

- Smolanalyst is currently restricted to importing only `pandas` and `matplotlib`.
- It can write files using these libraries, but only within the current working directory.
- Overwriting existing files is not allowed.

## TODO

- Remove the monkey patching of pandas and use a local docker enviroment
- Global CLI installation and package distribution
- Improve CLI configuration prompting and look
- Integrate SciPy for statistical analysis
- Implement regular testing to continuously evaluate Smolanalyst’s performance 🚀

```

```
