from langchain_core.messages import ToolMessage, AIMessage
import json


def print_tools_used(response):
    """
    Extract and print tool names used in a single LangChain agent response.
    """
    tool_names = {
        msg.name for msg in response["messages"]
        if isinstance(msg, ToolMessage)
    }

    if tool_names:
        print(f"Tools used: {', '.join(tool_names)}")
    else:
        print("Tools used: none")


def print_ai_metadata(response):
    """
    Print metadata from AIMessage objects in the agent response.
    """
    messages = response.get("messages", [])
    
    found = False
    for i, msg in enumerate(messages):
        if isinstance(msg, AIMessage):
            found = True
            print(f"\n Metadata from AIMessage #{i}:")
            print(json.dumps(msg.response_metadata, indent=2))
    
    if not found:
        print("No AIMessage with metadata found in this response.")
