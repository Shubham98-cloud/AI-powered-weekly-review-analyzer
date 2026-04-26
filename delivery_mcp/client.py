import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.sse import sse_client
from typing import Optional, Union

class MCPClient:
    def __init__(self, target: Union[str, StdioServerParameters]):
        """
        target can be a URL string (for SSE) or StdioServerParameters (for local process).
        """
        self.target = target
        self.session: Optional[ClientSession] = None
        self._exit_stack = None

    async def __aenter__(self):
        self._exit_stack = asyncio.ExitStack()
        
        if isinstance(self.target, str) and (self.target.startswith("http://") or self.target.startswith("https://")):
            # SSE Transport for remote servers like Alpha Vantage
            read, write = await self._exit_stack.enter_async_context(sse_client(self.target))
        else:
            # Stdio Transport for local servers
            read, write = await self._exit_stack.enter_async_context(stdio_client(self.target))
            
        self.session = await self._exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._exit_stack:
            await self._exit_stack.aclose()

async def call_mcp_tool(target: Union[str, StdioServerParameters], tool_name: str, arguments: dict):
    """
    Helper to call a specific tool on an MCP server (Stdio or SSE).
    """
    async with MCPClient(target) as session:
        result = await session.call_tool(tool_name, arguments)
        return result
