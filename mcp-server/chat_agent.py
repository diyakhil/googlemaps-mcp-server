from typing import Dict, List
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import os
import json
import redis
import asyncio
from dotenv import load_dotenv

#don't need to explicity set the key, it applies to the env here
load_dotenv()
os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")

class ChatAgent:
    #we are using a Redis database as a cache here
    #redis_db=0 selects database number 0, which is the default database --> redis comes with 16 dbs by default
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_db: int = 0):
        """Initialize the ChatAgent with Redis connection for memory management."""
        redis_host = os.getenv("REDIS_HOST") #adding first option for Docker
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        self.mcp_client = None
        self.agent = None
        self._initialized = False
    
    async def _initialize_agent(self):
        """Initialize the MCP client and agent (done once)."""
        #setting the instance variables of the class for mcp creation

        self.mcp_client = MultiServerMCPClient(
            {
                "driverassistant": {
                    "command": "python",
                    "args": ["mcp_server.py"],
                    "transport": "stdio",
                }
            }
        )

        tools = await self.mcp_client.get_tools()

        model = ChatGroq(
            model="qwen/qwen3-32b",
            max_tokens=2000,
            temperature=0.1
        )

        system_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a concise assistant. Follow these rules:
                1. Use tools IMMEDIATELY when they match the user's request
                2. Be as brief as possible in responses
                3. Skip unnecessary explanations
                4. Call tools directly without asking for permission"""),
            ("placeholder", "{messages}")
        ])

        self.agent = create_react_agent(model, tools, prompt=system_prompt)
        print("Agent initialized successfully")
    
    def get_memory_key(self, session_id: str) -> str:
        """Generate Redis key for session memory."""
        return f"chat_session:{session_id}"
    
    #returns a List[Dict] because langchain expects data in this format:
    #{"role": "user", "content": "Hello, how are you?"}
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Retrieve conversation history from Redis."""
        key = self.get_memory_key(session_id)
        messages_json = self.redis_client.get(key)
        if messages_json:
            return json.loads(messages_json)
        return []
    
    def save_conversation_history(self, session_id: str, messages: List[Dict], ttl_seconds: int = 3600):
        """Save conversation history to Redis with TTL."""
        key = self.get_memory_key(session_id)
        #redis can only store strings, which is why we have to do json.dumps
        self.redis_client.setex(key, ttl_seconds, json.dumps(messages))

    def clear_conversation_history(self, session_id: str):
        """Clear conversation history for a session."""
        key = self.get_memory_key(session_id)
        self.redis_client.delete(key)

    async def chat(self, prompt: str, session_id: str) -> Dict:     
        max_history_length = 10
        memory_ttl_seconds = 3600

        if not self._initialized:
            await self._initialize_agent()
            self._initialized = True

        messages = self.get_conversation_history(session_id)
        messages.append({"role": "user", "content": prompt})

        if len(messages) > max_history_length * 2:
            messages = messages[-(max_history_length * 2):]

        try:
            # Agent handles the entire ReAct loop internally
            response = await self.agent.ainvoke({"messages": messages})

            # Extract the final response
            if "messages" in response and response["messages"]:
                last_message = response["messages"][-1]
                agent_reply = last_message.content
            else:
                agent_reply = "Error: No response from agent"
            
            # Save conversation history
            messages.append({"role": "assistant", "content": agent_reply})
            self.save_conversation_history(session_id, messages, memory_ttl_seconds)
            
            return {
                "response": agent_reply,
                "session_id": session_id,
                "message_count": len(messages),
                "success": True
            }
        
        except Exception as e:
            return {
                "response": f"Error processing request: {str(e)}",
                "session_id": session_id,
                "success": False,
                "error": str(e)
            }

chat_agent = ChatAgent()

async def process_chat_message(prompt: str, session_id: str) -> Dict:
    return await chat_agent.chat(prompt, session_id)

async def main():
    """Example usage of the chat function."""

    #can use the same session id everytime because of the ttl feature that will eliminate data after time limit
    session_id = "test_session_123"
    
    # Test conversation
    test_messages = [
        "how long is the drive from qahwah house rva to grit coffee rva?"
    ]
    
    for message in test_messages:
        print(f"User: {message}")
        result = await process_chat_message(message, session_id)
        print(f"Assistant: {result['response']}")
        print(f"Message count: {result['message_count']}\n")
    
    # Clear history when done, uncomment to clear history
    #chat_agent.clear_conversation_history(session_id)

if __name__ == "__main__":
    asyncio.run(main())