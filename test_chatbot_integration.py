#!/usr/bin/env python3
"""
Test script for the complete Blockchain Chatbot integration
"""

import asyncio
import os
from blockchain_chatbot_mcp_v3 import BlockchainChatbotMCPv3
from mcp import ClientSession


async def test_full_integration():
    """
    Test the complete integration including LLM
    """
    print("🧪 Testing full chatbot integration...")
    
    # Check if Groq API key is available
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("   Please set GROQ_API_KEY in your .env file or environment")
        print("   Get your API key from: https://console.groq.com/keys")
        return False
    else:
        print("✅ Found GROQ_API_KEY in environment")
    
    chatbot = BlockchainChatbotMCPv3()
    
    try:
        # Test MCP connection
        transport = await chatbot.create_mcp_session()
        
        async with transport as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await chatbot.initialize_session(session)
                
                print("✅ MCP connection successful")
                print(f"   Available tools: {len(chatbot.available_tools)}")
                
                # Test simple tool execution
                result = await chatbot.execute_mcp_tool(session, "list_databases", {})
                print(f"✅ Tool execution successful: {result}")
                
                # Test LLM response generation (without tool calls)
                test_message = "Hello, can you help me understand blockchain data?"
                llm_response = await chatbot.get_llm_response(test_message, [])
                print(f"✅ LLM response successful: {llm_response[:100]}...")
                
                # Test a simple blockchain question
                blockchain_question = "How many databases are available?"
                response = await chatbot.process_conversation_turn(
                    session, blockchain_question, []
                )
                print(f"✅ Full conversation turn successful")
                print(f"   Question: {blockchain_question}")
                print(f"   Response: {response[:200]}...")
                
                return True
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_full_integration())
    if success:
        print("\n🎉 All tests passed! The chatbot is ready to use.")
        print("   Run: python blockchain_chatbot_mcp_v3.py")
    else:
        print("\n💥 Some tests failed. Please check the configuration.") 