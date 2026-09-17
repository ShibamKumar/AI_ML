import asyncio
import sys
from collections.abc import Sequence
from pathlib import Path

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


async def _get_tools_async() -> Sequence[BaseTool]:
    base_dir = Path(__file__).resolve().parent
    weather_server = str(base_dir / "mcp_servers" / "weather_server.py")
    currency_server = str(base_dir / "mcp_servers" / "currency_server.py")

    client = MultiServerMCPClient(
        {
            "weather": {
                "command": sys.executable,
                "args": [weather_server],
                "transport": "stdio",
            },
            "currency": {
                "command": sys.executable,
                "args": [currency_server],
                "transport": "stdio",
            },
        }
    )
    return await client.get_tools()


def get_mcp_tools() -> Sequence[BaseTool]:
    return asyncio.run(_get_tools_async())


def call_tool(tools: Sequence[BaseTool], name: str, tool_input: dict) -> str:
    for tool in tools:
        if tool.name == name:
            result = asyncio.run(tool.ainvoke(tool_input))
            return str(result)
    raise ValueError(f"Tool {name} not found")
