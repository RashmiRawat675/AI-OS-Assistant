import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langchain.mcp import MCPAdapter
from langgraph.checkpoint.memory import InMemorySaver


# Load .env from Ai_Engineer folder
env_path = Path(__file__).resolve().parents[3] / ".env"
load_dotenv(env_path)


def is_directory_listing_request(text: str) -> bool:
    """Detect common requests for a directory listing."""

    text = text.lower()

    listing_phrases = (
        "kaun-kaun si files",
        "kaun kaun si files",
        "files aur folders",
        "files and folders",
        "folder mein kaun",
        "directory mein kaun",
        "list files",
        "list directory",
        "folder contents",
        "exact names",
    )

    return any(phrase in text for phrase in listing_phrases)


def extract_listing_entries(tool_result):
    """Extract the original structured result from an MCP tool response."""

    artifact = getattr(tool_result, "artifact", None)

    if artifact is None and isinstance(tool_result, dict):
        artifact = tool_result.get("artifact", tool_result)

    if isinstance(artifact, dict):
        structured = artifact.get("structured_content", {})

        if isinstance(structured, dict):
            result = structured.get("result")
            if isinstance(result, list):
                return result

    # Fallback: inspect content blocks if structured data is unavailable.
    content = getattr(tool_result, "content", None)

    if isinstance(content, list):
        entries = []

        for block in content:
            if not isinstance(block, dict):
                continue

            text_value = block.get("text", "")

            if not text_value:
                continue

            try:
                parsed = json.loads(text_value)
                if isinstance(parsed, list):
                    entries.extend(parsed)
                else:
                    entries.append(parsed)
            except (json.JSONDecodeError, TypeError):
                entries.append(text_value)

        if entries:
            return entries

    return None


def print_listing(entries):
    """Print directory entries without asking the LLM to rewrite names."""

    print("\nAssistant: Exact directory entries\n")

    for entry in entries:
        if isinstance(entry, dict):
            if "error" in entry:
                print(f"Error: {entry['error']}")
                continue

            name = entry.get("name")
            entry_type = entry.get("type")

            if name is not None:
                if entry_type:
                    print(f"- {name} [{entry_type}]")
                else:
                    print(f"- {name}")
            else:
                print(f"- {entry}")

        else:
            # Preserve the original value returned by the tool.
            print(f"- {entry}")


async def main():

    # MCP server configuration
    server_path = (
        Path(__file__).resolve().parents[1]
        / "mcp_servers"
        / "filesystem"
        / "server.py"
    )

    # Connect LangChain to MCP server
    async with MCPAdapter(server_path) as adapter:

        tools = await adapter.list_tools()

        print("Available MCP tools:")
        for tool in tools:
            print("-", tool.name)

        # Create Groq model
        model = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
        )

        system_prompt = r"""
You are a helpful AI OS Assistant.

Available filesystem tools:
- list_directory: list files and folders.
- read_file: read a text file.
- write_file: create a new text file.

Rules:
1. Choose the appropriate tool for the request.
2. Never claim a tool succeeded unless its result confirms success.
3. Never invent file contents or tool results.
4. Only work inside C:\Users\HP\Ai_Engineer.
5. Never read or reveal .env files, API keys, passwords, or secrets.
6. write_file creates new files only and cannot overwrite existing files.
7. Ask for clarification if a request is ambiguous.
8. Explain results clearly and concisely.
9. Use the minimum number of tool calls needed.
10. Report empty files as empty; do not repeatedly read them.
11. Do not repeat a tool call unless necessary.
12. Preserve exact filenames, paths, values, and tool results.
13. Never merge, rename, omit, or invent directory entries.

Language rules:
- Match the user's language and style.
- For Hinglish, reply naturally in Roman script.
- For English, reply in English.
- For Hindi written in Devanagari, reply in Devanagari.
- Keep technical terms, code, paths, and tool names unchanged.
- Before reading a file, verify that the path is a file.
  If the user mentions a folder, list that folder first.
"""

        checkpointer = InMemorySaver()

        agent = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            checkpointer=checkpointer,
        )

        print("\nAI OS Assistant is ready!")
        print("Type 'exit' or 'quit' to stop.\n")

        while True:
            user_text = input("You: ").strip()

            if user_text.lower() in {"exit", "quit"}:
                print("Assistant: Goodbye!")
                break

            if not user_text:
                continue

            config = {
                "configurable": {
                    "thread_id": "rashmi-ai-os-session"
                }
            }

            user_input = {
                "messages": [
                    {
                        "role": "user",
                        "content": user_text,
                    }
                ]
            }

            listing_request = is_directory_listing_request(user_text)
            listing_entries = None
            streamed_text = []

            print("\n--- Live Agent Activity ---\n")

            async for event in agent.astream_events(
                user_input,
                config=config,
                version="v2",
            ):
                event_name = event["event"]

                if event_name == "on_tool_start":
                    tool_name = event["name"]
                    tool_args = event["data"].get("input", {})

                    print(f"\n[TOOL START] {tool_name}")
                    print(f"Arguments: {tool_args}")

                elif event_name == "on_tool_end":
                    tool_name = event["name"]
                    tool_result = event["data"].get("output", "")

                    print(f"\n[TOOL RESULT] {tool_name}")
                    print(tool_result)

                    if (
                        tool_name == "list_directory"
                        and listing_request
                    ):
                        listing_entries = extract_listing_entries(
                            tool_result
                        )

                elif event_name == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    content = chunk.content

                    if isinstance(content, str) and content:
                        streamed_text.append(content)

                        if not listing_request:
                            print(content, end="", flush=True)

                    elif isinstance(content, list):
                        for block in content:
                            if (
                                isinstance(block, dict)
                                and block.get("type") == "text"
                            ):
                                text_chunk = block.get("text", "")

                                if text_chunk:
                                    streamed_text.append(text_chunk)

                                    if not listing_request:
                                        print(
                                            text_chunk,
                                            end="",
                                            flush=True,
                                        )

            # Print the listing once, after all events have finished.
            if listing_request:
                if isinstance(listing_entries, list):
                    print_listing(listing_entries)
                else:
                    print(
                        "\nAssistant: Structured directory data "
                        "was unavailable."
                    )
                    if streamed_text:
                        print("Agent response:", "".join(streamed_text))

            print("\n\n--- Agent Run Complete ---\n")


if __name__ == "__main__":
    asyncio.run(main())
