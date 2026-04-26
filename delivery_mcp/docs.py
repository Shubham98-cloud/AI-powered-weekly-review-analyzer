from mcp import StdioServerParameters
from .client import call_mcp_tool

async def deliver_to_google_docs(
    markdown_content: str, 
    doc_id: str, 
    mcp_config: dict
):
    """
    Appends the report to a Google Doc using the Google Docs MCP server.
    """
    print(f"Delivering report to Google Doc: {doc_id}...")
    
    # Tool name might vary based on the specific MCP server implementation
    # Common tool name for appending: "create_content" or "update_document"
    # We'll use "create_content" as per common Google Docs MCP patterns
    try:
        server_params = StdioServerParameters(
            command=mcp_config["command"],
            args=mcp_config["args"],
            env=None
        )
        result = await call_mcp_tool(
            target=server_params,
            tool_name="create_content",
            arguments={
                "document_id": doc_id,
                "content": markdown_content,
                "append": True
            }
        )
        print(f"Docs Delivery Result: {result.content}")
        return True
    except Exception as e:
        print(f"Error delivering to Google Docs: {e}")
        return False
