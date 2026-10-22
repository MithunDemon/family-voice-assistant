import asyncio
import json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def test_mcp_client():
    url = "http://127.0.0.1:8001/mcp"
    print(f"Connecting to MCP server at {url} over Streamable HTTP...")

    async with streamable_http_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            print("Initializing session...")
            await session.initialize()

            print("\n1. Listing available tools from MCP server:")
            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                print(f"  • {tool.name}: {tool.description.strip().splitlines()[0]}")

            print("\n2. Calling tool 'add_grocery_item':")
            add_result = await session.call_tool(
                name="add_grocery_item",
                arguments={"item": "blueberries", "quantity": "2 pints"}
            )
            print("Result:", add_result.content)

            print("\n3. Calling tool 'list_groceries':")
            list_result = await session.call_tool(
                name="list_groceries",
                arguments={}
            )
            print("Result:", list_result.content)

            print("\nAll MCP tests passed successfully!")


if __name__ == "__main__":
    asyncio.run(test_mcp_client())
