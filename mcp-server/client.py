from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq

from dotenv import load_dotenv
load_dotenv()

import asyncio

async def main():
    client=MultiServerMCPClient(
        {
            "driverassistant":{
                "command":"python",
                "args":["main.py"],
                "transport":"stdio",
            
            }

        }
    )

    import os
    os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

    tools=await client.get_tools()
    model=ChatGroq(model="qwen/qwen3-32b")

    agent=create_react_agent(
        model,tools
    )

    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the time to get from qahwah house richmond to grit coffee scott's addition"}]}
    )

    print("Response:", response['messages'][-1].content)


asyncio.run(main())