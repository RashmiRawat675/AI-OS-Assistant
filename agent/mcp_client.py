import asyncio

from mcp import Client, StdioServerParameters


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_servers/filesystem/server.py"],
    )

    async with Client(server_params) as client:
        print("Connected to MCP Server!")

        tools = await client.list_tools()

        print("\nAvailable tools:")
        print(tools)

        result = await client.call_tool(
          "list_directory",
           {
             "path": r"C:\Users\HP\Ai_Engineer"
           }
        )

        print("\nTool Result:")
        print(result)

if __name__ == "__main__":
    asyncio.run(main())