from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv
import asyncio
from debug import print_tools_used, print_ai_metadata

load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


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

    tools=await client.get_tools()
    model=ChatGroq(
        model="qwen/qwen3-32b",
        max_tokens=1024, 
        temperature=0.1 
        )

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
        # print("Raw Response Was", response) #Debugging purposes to see token usage 
        # print_tools_used(response)
        # print_ai_metadata(response)
        messages.append({"role": "assistant", "content": agent_reply})

asyncio.run(main())