"""
DeepWiki + Gemini demo, using LangChain's MultiServerMCPClient
wrapper instead of the raw mcp SDK. Much less code, but it pulls in
LangChain/LangGraph as dependencies and hides the protocol details.

pip install langchain-mcp-adapters langchain-google-genai langgraph
"""
import asyncio
from dotenv import load_dotenv
load_dotenv()

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent

DEEPWIKI_URL = "https://mcp.deepwiki.com/mcp"

async def main():
    client = MultiServerMCPClient(
        {
            "deepwiki" : {
                # Remote server -> streamable_http, not stdio.
                # (stdio/"command" is only for servers you run locally,
                # e.g. a python script you wrote yourself.)
                "url" : DEEPWIKI_URL,
                "transport" : "streamable_http"
            }
        }
    )

    tools = await client.get_tools()

    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

    agent = create_agent(
        model=model,
        tools = tools
    )

    for tool in tools:
        print(f"[{tool.name}] : {tool.description}")
        print("="*60)

    print("Repo Research Assistant (LangChain + Gemini). Type 'quit' to exit.\n")
    while True:
        query = input("You: ").strip()
        if query.lower() in ("quit","exit"):
            break
        result = await agent.ainvoke({"messages": [{"role": "user","content": query}]})
        print(f"Assistant : {result['messages'][-1].content}\n")

if __name__ == "__main__":
    asyncio.run(main())