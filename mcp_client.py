import asyncio
import httpx
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Load configuration
with open("config.json") as f:
    config = json.load(f)


async def chat_with_ollama(prompt: str, model: str = None) -> str:
    """Send a prompt to Ollama and get the response."""
    if model is None:
        model = config["models"][0]["name"]
    
    endpoint = config["models"][0]["endpoint"]
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{endpoint}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error from Ollama: {response.status_code}"


async def main():
    """Main function to run the MCP client with Ollama."""
    
    # Configure the MCP server connection from config
    server_params = StdioServerParameters(
        command="python",
        args=[config["entrypoint"]],
        env=None
    )
    
    model_name = config["models"][0]["name"]
    print(f"Starting MCP Client with Ollama ({model_name})...")
    print("-" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # List available tools from the MCP server
            tools_list = await session.list_tools()
            print(f"\nAvailable tools from MCP server:")
            for tool in tools_list.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            print("\n" + "=" * 60)
            print("Chat with Ollama + Wikipedia MCP Tool")
            print("Type 'quit' or 'exit' to end the session")
            print("=" * 60 + "\n")
            
            # Prepare tool descriptions for the LLM
            tool_descriptions = "\n".join([
                f"- {tool.name}: {tool.description}" 
                for tool in tools_list.tools
            ])
            
            system_prompt = f"""You are a helpful assistant with access to the following tools:

{tool_descriptions}

When a user asks about a topic that could benefit from Wikipedia information, respond with:
TOOL_CALL: wikipedia_summary("topic_name")

Otherwise, answer normally. Be concise and helpful."""
            
            conversation_history = []
            
            while True:
                # Get user input
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Add user message to history
                conversation_history.append(f"User: {user_input}")
                
                # Build the full prompt with context
                full_prompt = f"{system_prompt}\n\nConversation:\n" + "\n".join(conversation_history[-6:]) + "\nAssistant: "
                
                # Get response from Ollama
                print("\nAssistant: ", end="", flush=True)
                ollama_response = await chat_with_ollama(full_prompt)
                
                # Check if the LLM wants to use a tool
                if "TOOL_CALL:" in ollama_response and "wikipedia_summary" in ollama_response:
                    # Extract the topic from the tool call
                    try:
                        # Simple parsing - look for content between quotes
                        start = ollama_response.find('wikipedia_summary("') + len('wikipedia_summary("')
                        end = ollama_response.find('")', start)
                        topic = ollama_response[start:end]
                        
                        print(f"[Fetching Wikipedia summary for: {topic}]")
                        
                        # Call the MCP tool
                        result = await session.call_tool("wikipedia_summary", arguments={"topic": topic})
                        
                        # Extract the content from the result
                        tool_output = ""
                        for content in result.content:
                            if hasattr(content, 'text'):
                                tool_output = content.text
                        
                        print(f"\n{tool_output}\n")
                        
                        # Add to conversation history
                        conversation_history.append(f"Assistant: [Retrieved Wikipedia info about {topic}]")
                        conversation_history.append(f"Tool Result: {tool_output}")
                        
                        # Ask Ollama to summarize or use the information
                        summary_prompt = f"{system_prompt}\n\nConversation:\n" + "\n".join(conversation_history[-6:]) + f"\n\nPlease provide a helpful response based on the Wikipedia information above.\nAssistant: "
                        
                        final_response = await chat_with_ollama(summary_prompt)
                        print(final_response)
                        conversation_history.append(f"Assistant: {final_response}")
                        
                    except Exception as e:
                        print(f"Error parsing tool call: {e}")
                        print(ollama_response)
                        conversation_history.append(f"Assistant: {ollama_response}")
                else:
                    # No tool call, just print the response
                    print(ollama_response)
                    conversation_history.append(f"Assistant: {ollama_response}")
                
                print()


if __name__ == "__main__":
    asyncio.run(main())
