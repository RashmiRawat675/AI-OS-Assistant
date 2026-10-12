# AI OS Assistant

A Python-based AI assistant that uses the Model Context Protocol (MCP) to interact with local files and directories through controlled tools.

## Features

- **MCP Tool Integration:** Connects an AI agent to filesystem tools.
- **Directory Listing:** Lists files and folders in the configured workspace.
- **File Reading:** Reads file contents through MCP tools.
- **File Creation:** Creates files through filesystem tool operations.
- **Workspace Security:** Tested restrictions on access outside the permitted workspace.
- **Overwrite Protection:** Tested protection that preserves existing file contents.
- **LLM Integration:** Uses LangChain and Groq-related dependencies.

## Tech Stack

- Python 3.12+
- Model Context Protocol (MCP)
- LangChain
- Groq
- python-dotenv
- uv

## Project Structure

```text
AI_OS_Assistant/
├── agent/
│   ├── agent.py
│   └── mcp_client.py
├── mcp_servers/
│   └── filesystem/
│       └── server.py
├── src/
│   └── ai_os_assistant/
├── .gitignore
├── pyproject.toml
├── README.md
└── uv.lock
```

## Setup

1. Install Python 3.12 or later.
2. Install uv.
3. Clone this repository.
4. Open a terminal in the project directory and install dependencies:

```bash
uv sync
```

5. Configure the required environment variables locally according to the application code. Never commit API keys or `.env` files.

6. Run the assistant using the launch command configured for the project.

## Security and Testing

The following manual test cases have been verified:

- Directory listing
- File reading
- Blocking access outside the permitted workspace
- Existing-file overwrite protection

Additional edge cases and error-handling tests remain to be verified.

## Author

**Rashmi Rawat**

GitHub: [RashmiRawat675](https://github.com/RashmiRawat675)
