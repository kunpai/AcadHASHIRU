---
title: HashiruAI
emoji: 🍆
colorFrom: green
colorTo: yellow
sdk: gradio
sdk_version: 5.31.0
python_version: 3.11.9
app_file: start.py
pinned: false
---

# HASHIRU: Hierarchical Agent System for Hybrid Intelligent Resource Utilization

![HASHIRU_ARCH](HASHIRU_ARCH.png)

## Project Overview

This project provides a framework for creating and managing AI agents and tools. It includes features for managing resource and expense budgets, loading tools and agents, and interacting with various language models.

## Directory Structure

*   **src/**: Contains the source code for the project.
    *   **tools/**: Contains the code for the tools that can be used by the agents.
        *   **default\_tools/**: Contains the default tools provided with the project.
        *   **user\_tools/**: Contains the tools created by the user.
    *   **config/**: Contains configuration files for the project.
    *   **utils/**: Contains utility functions and classes used throughout the project.
    *   **models/**: Contains the configurations and system prompts for the agents. Includes `models.json` which stores agent definitions.
    *   **manager/**: Contains the core logic for managing agents, tools, and budgets.
        *   `agent_manager.py`: Manages the creation, deletion, and invocation of AI agents. Supports different agent types like Ollama, Gemini, and Groq.
        *   `budget_manager.py`: Manages the resource and expense budgets for the project.
        *   `tool_manager.py`: Manages the loading, running, and deletion of tools.
        *   `llm_models.py`: Defines abstract base classes for different language model integrations.
    *   **data/**: Contains data files, such as memory and secret words.

## Key Components

*   **Agent Management:** The `AgentManager` class in `src/manager/agent_manager.py` is responsible for creating, managing, and invoking AI agents. It supports different agent types, including local (Ollama) and cloud-based (Gemini, Groq) models.
*   **Tool Management:** The `ToolManager` class in `src/manager/tool_manager.py` handles the loading and running of tools. Tools are loaded from the `src/tools/default_tools` and `src/tools/user_tools` directories.
*   **Budget Management:** The `BudgetManager` class in `src/manager/budget_manager.py` manages the resource and expense budgets for the project. It tracks the usage of resources and expenses and enforces budget limits.
*   **Model Integration:** The project supports integration with various language models, including Ollama, Gemini, and Groq. The `llm_models.py` file defines abstract base classes for these integrations.

## Usage

To use the project, follow these steps:
1.  Install the required dependencies by running `pip install -r requirements.txt`.
2.  Start the application by running `python app.py`. This will launch a web interface where you can interact with the agents and tools.

By default, on running `python app.py`, you would need to authenticate with Auth0. But, this can be overriden through the CLI argument `--no-auth` to skip authentication.

To use the project with additional tools and agents, you need to:

1.  Configure the budget in `src/tools/default_tools/agent_cost_manager.py`.
2.  Create tools and place them in the `src/tools/default_tools` or `src/tools/user_tools` directories.

Please note that by default, we do provide a lot of pre-defined tools and agents, so you may not need to create your own tools unless you have specific requirements.

## Model Support
The project supports the following language model integrations:
- **Ollama**: Local model management and invocation.
- **Gemini**: Cloud-based model management and invocation from Google.
- **Groq**: Cloud-based model management and invocation from Groq.
- **Lambda**: Cloud-based model management and invocation from Lambda Labs.

## Acknowledgements
We would like to thank Hugging Face, Groq and Lambda Labs for sponsoring this project and providing the necessary resources for development.

## Contributing

Contributions are welcome! Please submit pull requests with bug fixes, new features, or improvements to the documentation.