# AppstoreDataAgent Crew

Welcome to the AppstoreDataAgent Crew project, powered by [crewAI](https://crewai.com). This template is designed to help you set up a multi-agent AI system with ease, leveraging the powerful and flexible framework provided by crewAI. Our goal is to enable your agents to collaborate effectively on complex tasks, maximizing their collective intelligence and capabilities.

## Installation

Ensure you have Python >=3.10 <3.14 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies:

```bash
uv pip install -e .
```

(Optional) Lock the dependencies and install them by using the CLI command:
```bash
crewai install
```
### Customizing

**Add your `OPENAI_API_KEY` into the `.env` file**

- Modify `src/appstore_data_agent/config/agents.yaml` to define your agents
- Modify `src/appstore_data_agent/config/tasks.yaml` to define your tasks
- Modify `src/appstore_data_agent/crew.py` to add your own logic, tools and specific args
- Modify `src/appstore_data_agent/main.py` to add custom inputs for your agents and tasks

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder of your project:

```bash
$ crewai run
```

This command initializes the appstore_data_agent Crew, assembling the agents and assigning them tasks as defined in your configuration.

This example, unmodified, will run the create a `report.md` file with the output of a research on LLMs in the root folder.

## Running Tests

After installing your project in editable mode using `uv pip install -e .`, you can run your tests with `pytest`.

To run all tests:

```bash
uv run pytest
```

To run a specific test file (e.g., `tests/test_custom_tool.py`):

```bash
uv run pytest tests/test_custom_tool.py
```

## Understanding Your Crew

The appstore_data_agent Crew is composed of multiple AI agents, each with unique roles, goals, and tools. These agents collaborate on a series of tasks, defined in `config/tasks.yaml`, leveraging their collective skills to achieve complex objectives. The `config/agents.yaml` file outlines the capabilities and configurations of each agent in your crew.

## FAQ

### `ModuleNotFoundError: No module named 'src'` when running tests

This error occurs when Python cannot find your project's `src` package. This is usually resolved by installing your project in "editable" mode, which creates a link to your source code in Python's path. Ensure you run:

```bash
uv pip install -e .
```

If you are not using `uv` or still encounter issues, you might need to temporarily add your project root to the `PYTHONPATH` environment variable. For example, if you are in the project's root directory:

```bash
export PYTHONPATH=$PWD:$PYTHONPATH
uv run pytest tests/test_intent_identifier.py
```

Alternatively, you can add it for a single command:

```bash
PYTHONPATH=$PWD pytest tests/test_intent_identifier.py
```

This ensures Python can find the `src` directory and its contents.

## Support

For support, questions, or feedback regarding the AppstoreDataAgent Crew or crewAI.
- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
