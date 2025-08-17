#!/usr/bin/env python3
"""
Simple OpenAI Chat Script with Native MCP Integration

This script creates a chat interface that uses OpenAI's native MCP support
to connect to the Playwright MCP server.

Installation:
    pip install openai python-dotenv

Environment:
    Create a .env file with:
    OPENAI_API_KEY=your_openai_api_key_here

Usage:
    python chat.py
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

class ChatBot:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.conversation_history = []
        self.mcp_config = {
            "type": "mcp",
            "server_label": "playwright",
            "server_url": "https://playwrightmcp.ice.computer/mcp",
            "require_approval": "never",
        }
        
    def chat_with_openai(self, message: str) -> str:
        """Send message to OpenAI with MCP tools and get response"""
        try:
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            # Create the response using OpenAI's MCP integration
            resp = self.client.responses.create(
                model="gpt-4o",
                tools=[self.mcp_config],
                input=message,
                # You can also include conversation history if needed
                # messages=self.conversation_history[-10:]  # Keep last 10 messages
            )
            
            ai_response = resp.output_text
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("🤖 OpenAI Chat with Playwright MCP Integration")
        print("=" * 50)
        print("✅ Using OpenAI's native MCP support")
        print(f"🌐 Connected to: {self.mcp_config['server_url']}")
        print("\n💬 Chat started! Type 'quit' to exit.")
        print("🔧 Ask me to do web automation tasks like taking screenshots, navigating to websites, etc!")
        print("-" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get AI response
                print("🤖 AI: ", end="", flush=True)
                response = self.chat_with_openai(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main function"""
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with: OPENAI_API_KEY=your_key_here")
        return
    
    # Create and start chatbot
    chatbot = ChatBot()
    chatbot.start_chat()


if __name__ == "__main__":
    main()