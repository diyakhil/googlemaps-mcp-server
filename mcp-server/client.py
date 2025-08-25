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

    # Commenting out to show message array approach to memory 
    # response = await agent.ainvoke(
    #     {"messages": [{"role": "user", "content": "what is the time to get from qahwah house richmond to grit coffee scott's addition"}]}
    # )
    # print("Response:", response['messages'][-1].content)

    # Maintain a global array for messages to maintain state 
    messages = []

    print("Chat is ready. Type 'exit' or 'quit' to stop.\n")

    # Continuous chat sequence until key word is given 
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("Ending chat. Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})
        response = await agent.ainvoke({"messages": messages})
        agent_reply = response["messages"][-1].content
        print("Assistant:", agent_reply)
        messages.append({"role": "assistant", "content": agent_reply})

asyncio.run(main())