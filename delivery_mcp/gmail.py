from mcp import StdioServerParameters
from .client import call_mcp_tool

async def deliver_to_gmail(
    html_content: str, 
    subject: str, 
    recipient: str, 
    mcp_config: dict
):
    """
    Sends an email using the Gmail MCP server.
    """
    print(f"Sending pulse email to {recipient}...")
    
    try:
        server_params = StdioServerParameters(
            command=mcp_config["command"],
            args=mcp_config["args"],
            env=None
        )
        result = await call_mcp_tool(
            target=server_params,
            tool_name="send_message",
            arguments={
                "recipient": recipient,
                "subject": subject,
                "body": html_content,
                "is_html": True
            }
        )
        print(f"Gmail Delivery Result: {result.content}")
        return True
    except Exception as e:
        print(f"Error delivering to Gmail: {e}")
        return False
