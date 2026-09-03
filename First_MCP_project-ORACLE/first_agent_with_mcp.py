"""
==========================================================
MCP + LangChain Agent — Before & After Comparison
==========================================================
This is the SAME agent as first_agent.py, but instead of
defining tools locally with @tool, it discovers them from
an MCP server at runtime.

THE KEY DIFFERENCE:
  ┌─────────────────────────────────────────────────┐
  │  BEFORE (first_agent.py):                    │
  │    Tools are hardcoded in the agent's code.     │
  │    Every agent must redefine the same tools.    │
  │    Changing a tool = changing every agent.       │
  │                                                 │
  │  AFTER (this file):                             │
  │    Tools live on an MCP server.                 │
  │    Any agent can discover & use them.           │
  │    Changing a tool = update one server.          │
  │    Tools are reusable across Claude, ChatGPT,   │
  │    Cursor, VS Code, and your own agents.        │
  └─────────────────────────────────────────────────┘

Prerequisites:
  pip install langchain langchain-openai langgraph
  pip install langchain-mcp-adapters mcp python-dotenv

Setup:
  Create a .env file with: OPENAI_API_KEY=sk-your-key-here

  Make sure mcp_math_server.py is in the same directory.

Usage:
  python first_agent_with_mcp.py
==========================================================
"""
import os
import asyncio
from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore",category=UserWarning)
load_dotenv()

# ─────────────────────────────────────────────
# STEP 1: Initialize the Model
# ─────────────────────────────────────────────
# ✅ SAME AS BEFORE — the model doesn't change.
# MCP only changes WHERE tools come from,
# not how the LLM reasons about them.

from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash"
)
# model = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

# ─────────────────────────────────────────────
# STEP 2: Define Your Tools
# ─────────────────────────────────────────────
#
# ❌ BEFORE (first_agent.py):
#    Tools were defined right here with @tool decorators.
#    Hardcoded, tightly coupled to this one agent file.
#
#    @tool
#    def add(a: float, b: float) -> float:
#        """Add two numbers together."""
#        return a + b
#
#    @tool
#    def multiply(a: float, b: float) -> float:
#        """Multiply two numbers together."""
#        return a * b
#
#    ... (every tool manually defined)
#    tools = [add, multiply, divide, square_root]
#
#
# ✅ AFTER (with MCP):
#    Tools are DISCOVERED from an MCP server at runtime.
#    No @tool decorators. No local function definitions.
#    The server could be local or running on another machine.
#    The SAME server works with Claude, ChatGPT, Cursor, etc.

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent


async def main():
    """
    Main async function — MCP connections are async because
    they involve I/O (spawning processes, network calls).
    """
     
    # ─────────────────────────────────────────
    # Connect to the MCP Server
    # ─────────────────────────────────────────
    # This is the NEW part. Instead of defining tools locally,
    # we point to an MCP server and let the adapter discover
    # all available tools automatically.
    #
    # The MultiServerMCPClient can connect to MULTIPLE servers
    # at once — imagine combining a math server + a GitHub
    # server + a database server, all in one agent!

    # Get the absolute path to the MCP server script

    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_path = os.path.join(current_dir,"mcp_math_server.py")

    client = MultiServerMCPClient(
         {
              "math":{
                   # The MCP server to connect to
                   "command": "python",
                   "args" : [server_path],
                   "transport" : "stdio"    # Local process (stdin/stdout)
              },
                # ── Want MORE tools? Just add more servers! ──
                # No code changes to the agent logic needed.
                #
                # "github": {
                #     "command": "npx",
                #     "args": ["-y", "@modelcontextprotocol/server-github"],
                #     "transport": "stdio",
                #     "env": {"GITHUB_TOKEN": os.getenv("GITHUB_TOKEN")},
                # },
                #
                # "weather": {
                #     "url": "http://localhost:8000/mcp",
                #     "transport": "http",       # Remote server
                # },
         }
    )

    # ─────────────────────────────────────────
    # Discover Tools from the MCP Server
    # ─────────────────────────────────────────
    # This is where the magic happens!
    # The client connects to the server, performs the MCP
    # handshake, and auto-discovers all available tools.
    # Each MCP tool is converted into a LangChain tool.

    tools = await client.get_tools()

    for t in tools:
        print(f"{t.name} : {t.description[:60]}...")

    # ─────────────────────────────────────────
    # STEP 3: Create the Agent
    # ─────────────────────────────────────────
    # ✅ SAME AS BEFORE — the agent creation is identical!
    # The agent doesn't know or care that tools came from MCP.
    # It just sees LangChain tools and uses them normally.
    
    agent = create_agent(
        model,
        tools = tools
    )

    # ─────────────────────────────────────────
    # STEP 4: Run the Agent
    # ─────────────────────────────────────────
    # ✅ SAME AS BEFORE — the run function is identical.

    async def run_agent(question: str):
        """Run the agent and print the execution trace. """
        print(f"User: {question}")
        print("-" * 50)

        result = await agent.ainvoke({
            "messages": [("user", question)]
        })

        print("agent : ",result["messages"][-1].content)

    await run_agent("What is 42 + 58?" )
    await run_agent(
        "I have a rectangle with width 12 and height 7. "
        "What is its area, and what is the square root of that area?"
    )


if __name__ =="__main__":
    asyncio.run(main())