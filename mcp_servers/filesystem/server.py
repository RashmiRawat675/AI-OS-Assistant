from pathlib import Path

from mcp.server.mcpserver import MCPServer


# Only allow access inside Ai_Engineer
ALLOWED_ROOT = Path(
    r"C:\Users\HP\Ai_Engineer"
).resolve()

# Create MCP server
mcp = MCPServer("Filesystem Server")


def get_safe_path(path: str) -> Path:
    """Resolve a path and prevent access outside the workspace."""

    target = Path(path).resolve()

    try:
        target.relative_to(ALLOWED_ROOT)
    except ValueError:
        raise ValueError(
            "Access denied: path is outside the allowed workspace."
        )

    return target

@mcp.tool()
def list_directory(path: str) -> list[dict[str, str]]:
    """List exact file and folder names inside an allowed directory."""

    try:
        directory = get_safe_path(path)

        if not directory.exists():
            return [{"error": f"Path does not exist: {path}"}]

        if not directory.is_dir():
            return [{"error": f"Path is not a directory: {path}"}]

        entries = []

        for item in sorted(directory.iterdir(), key=lambda entry: entry.name.lower()):
            entry_type = "directory" if item.is_dir() else "file"

            entries.append({
                "name": item.name,
                "type": entry_type,
            })

        return entries

    except (ValueError, OSError, RuntimeError) as exc:
        return [{"error": str(exc)}]

@mcp.tool()
def read_file(path: str) -> str:
    """Read a UTF-8 text file inside the allowed workspace."""

    try:
        file_path = get_safe_path(path)

        if not file_path.exists():
            return f"File does not exist: {path}"

        if not file_path.is_file():
            return f"Path is not a file: {path}"

        return file_path.read_text(encoding="utf-8")

    except (ValueError, OSError, RuntimeError) as exc:
        return str(exc)


@mcp.tool()
def write_file(path: str, content: str) -> str:
    """Create or update a UTF-8 text file inside the allowed workspace."""
    try:
        file_path = get_safe_path(path)

        if file_path.exists() and file_path.is_dir():
            return f"Path is a directory, not a file: {path}"

        file_path.parent.mkdir(parents=True, exist_ok=True)
        with file_path.open("x", encoding="utf-8") as file:
         file.write(content)

        return f"File written successfully: {file_path}"

    except (ValueError, OSError, RuntimeError) as exc:
        return str(exc)


if __name__ == "__main__":
    mcp.run()