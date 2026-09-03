"""
==========================================================
MCP Math Server — The "Tool Provider"
==========================================================
This server exposes the EXACT SAME tools that were
hardcoded in first_agent.py, but now they live here
as a reusable MCP server.

ANY MCP-compatible client can use these tools:
  - Your LangChain agent (first_agent_with_mcp.py)
  - Claude Desktop
  - ChatGPT
  - Cursor IDE
  - VS Code Copilot
  - Any custom MCP client

That's the whole point of MCP: define once, use everywhere.

Usage:
  This file is auto-launched by the agent script.
  To test standalone: python mcp_math_server.py
  To inspect:         fastmcp dev mcp_math_server.py
==========================================================
"""
from mcp.server.fastmcp import FastMCP
import math
import sys

# Create the MCP server
mcp = FastMCP("Math")

# ─────────────────────────────────────────────
# These are the SAME tools from first_agent.py
# but now exposed via MCP instead of @tool
# ─────────────────────────────────────────────

@mcp.tool() #decorater
def add(a: float,b:float) -> float: #a:float here float is the type hints
    """Add two numbers together. Use for addition operations. """ #docstring
    return a + b

@mcp.tool()
def multiply(a: float,b:float) -> float:
    """Multiply two numbers together. Use for multliplication operations. """
    print(f"[math-server] multiply(a={a},b={b})",file=sys.stderr)
    return a * b

@mcp.tool()
def divide(a: float,b:float) -> float:
    """Divide first numbers by the second. Return errorif divided by zero. """
    if b ==0:
        return "Error : Cannot divide by zero"
    print(f"[math-server] divide(a={a},b={b})",file=sys.stderr)
    return a/b

@mcp.tool()
def square_root(number:float) -> float:
    """Calculate the square root of the number. """
    if number < 0:
        return "Error : Cannot take square root of negative numbers"
    return math.sqrt(number)

# ─────────────────────────────────────────────
# Run the server
# ─────────────────────────────────────────────
# transport="stdio" means the server communicates via
# stdin/stdout — the agent launches it as a subprocess.

if __name__ == "__main__":
    mcp.run(transport="stdio")
