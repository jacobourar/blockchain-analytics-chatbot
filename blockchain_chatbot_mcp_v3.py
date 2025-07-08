#!/usr/bin/env python3
"""
Blockchain Analytics Chatbot - Phase 2
Fresh implementation using official Python MCP SDK

This implementation creates a bridge between Groq LLM and ClickHouse MCP server
using the official MCP SDK patterns.
"""

import os
import asyncio
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from groq import AsyncGroq
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()


@dataclass
class DatabaseSchema:
    """Database schema information for context"""
    
    def get_schema_context(self) -> str:
        return """
        ETHEREUM BLOCKCHAIN DATABASE SCHEMA (goteth_mainnet)
        
        You are analyzing Ethereum Proof-of-Stake consensus layer data. Key tables:
        
        1. t_validator_last_status (1.98M rows) - Current validator status
           - f_val_idx: Validator index (unique identifier)
           - f_epoch: Current epoch number
           - f_balance_eth: Validator balance in ETH
           - f_effective_balance: Effective balance for consensus (in wei)
           - f_status: Status code (1=active, 0=inactive)
           - f_slashed: Boolean indicating if validator was slashed
           
        2. t_block_metrics (11.96M rows) - Block production data
           - f_slot: Slot number (12-second intervals)
           - f_epoch: Epoch number (32 slots = 1 epoch)
           - f_proposer_index: Validator who proposed the block
           - f_proposed: Boolean indicating if block was actually proposed
           - f_attestations: Number of attestations in block
           
        3. t_pool_summary (65.6M rows) - Staking pool performance
           - f_pool_name: Name of staking pool
           - f_epoch: Epoch number
           - aggregated_rewards: Total rewards for pool in epoch
           - aggregated_effective_balance: Total effective balance
           
        4. t_epoch_metrics_summary (375K rows) - Network-wide metrics
           - f_epoch: Epoch number
           - f_num_vals: Number of active validators
           - f_total_balance_eth: Total ETH staked
           - f_num_att: Number of attestations
           
        5. t_block_rewards (7.6M rows) - Economic data
           - f_slot: Slot number
           - f_reward_fees: Transaction fees earned
           - f_burnt_fees: EIP-1559 burnt fees
           - f_cl_manual_reward: Consensus layer rewards
           
        QUERY GUIDELINES:
        - Always use LIMIT clauses (max 100 rows for display)
        - Use aggregate functions (COUNT, SUM, AVG) for large datasets
        - Field names are prefixed with f_ (e.g., f_val_idx, f_epoch)
        - Epochs are ~6.4 minutes, slots are 12 seconds
        - Current epoch is around 375000+
        - Balance fields may be in wei (divide by 1e18 for ETH) or ETH
        """


class MCPToolError(Exception):
    """Exception raised when MCP tool execution fails"""
    pass


class BlockchainChatbotMCPv3:
    """
    Blockchain analytics chatbot using official MCP SDK patterns
    """
    
    def __init__(self):
        # Initialize Groq LLM
        self.groq_client = AsyncGroq(
            api_key=os.getenv("GROQ_API_KEY"),
        )
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile")
        
        # MCP server configuration for ClickHouse
        self.mcp_server_params = StdioServerParameters(
            command="python",
            args=["-m", "mcp_clickhouse.main"],
            env=dict(os.environ)
        )
        
        # Database schema context
        self.schema = DatabaseSchema()
        
        # Available MCP tools (will be populated after connection)
        self.available_tools: List[Dict[str, Any]] = []
        
    async def create_mcp_session(self):
        """
        Create MCP session using proper async context manager pattern
        """
        print("🔌 Connecting to ClickHouse MCP server...")
        
        # Use proper async context manager pattern from official SDK
        return stdio_client(self.mcp_server_params)
    
    async def initialize_session(self, session: ClientSession):
        """
        Initialize MCP session and discover tools
        """
        await session.initialize()
        print("✅ MCP connection established and initialized")
        
        # Discover available tools
        await self._discover_tools(session)
    
    async def _discover_tools(self, session: ClientSession):
        """Discover and cache available MCP tools"""
        try:
            tools_result = await session.list_tools()
            self.available_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema if hasattr(tool, 'inputSchema') else {}
                }
                for tool in tools_result.tools
            ]
            
            print(f"🔧 Discovered {len(self.available_tools)} MCP tools:")
            for tool in self.available_tools:
                print(f"   - {tool['name']}: {tool['description']}")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not discover tools: {e}")
            self.available_tools = []
    
    async def execute_mcp_tool(self, session: ClientSession, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute an MCP tool and return the result
        """
        try:
            print(f"🔨 Executing MCP tool: {tool_name} with args: {arguments}")
            
            result = await session.call_tool(tool_name, arguments)
            
            if result.isError:
                raise MCPToolError(f"Tool execution failed: {result.content}")
            
            # Extract content from result
            if hasattr(result, 'content') and result.content:
                if isinstance(result.content, list) and len(result.content) > 0:
                    # Handle list of content items
                    content_item = result.content[0]
                    if hasattr(content_item, 'text'):
                        return content_item.text
                    elif hasattr(content_item, 'data'):
                        return content_item.data
                    else:
                        return str(content_item)
                else:
                    return str(result.content)
            else:
                return "Tool executed successfully but returned no content"
                
        except Exception as e:
            error_msg = f"MCP tool execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            raise MCPToolError(error_msg)
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the LLM"""
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in self.available_tools
        ])
        
        return f"""You are a blockchain analytics assistant with access to Ethereum consensus layer data.

{self.schema.get_schema_context()}

AVAILABLE MCP TOOLS:
{tools_description}

        INSTRUCTIONS:
1. When users ask questions about blockchain data, analyze what information you need
2. Use the appropriate MCP tools to query the database
3. For SQL queries, generate ClickHouse-compatible SQL with proper LIMIT clauses
4. Always explain your findings in clear, user-friendly language
5. If you need to make multiple queries, do them step by step

TOOL USAGE FORMAT:
When you need to use a tool, respond with:
TOOL_CALL: {{
    "tool_name": "tool_name_here",
    "arguments": {{"arg1": "value1", "arg2": "value2"}}
}}

IMPORTANT TOOL SIGNATURES:
- list_databases(): No parameters needed
- list_tables(database): Requires database name (e.g., "goteth_mainnet")
- run_select_query(query): Only requires SQL query string, database connection is already established

After receiving tool results, provide a comprehensive answer based on the data.
"""
    
    async def get_llm_response(self, user_message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Get response from Groq LLM
        """
        messages = [
            {"role": "system", "content": self._create_system_prompt()}
        ]
        
        # Add conversation history
        messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.groq_client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.1,  # Low temperature for precise analysis
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error getting LLM response: {str(e)}"
    
    def _extract_tool_call(self, llm_response: str) -> Optional[Dict[str, Any]]:
        """
        Extract tool call from LLM response if present
        """
        if "TOOL_CALL:" not in llm_response:
            return None
        
        try:
            # Find the JSON part after TOOL_CALL:
            tool_call_start = llm_response.find("TOOL_CALL:") + len("TOOL_CALL:")
            tool_call_json = llm_response[tool_call_start:].strip()
            
            # Extract JSON object
            if tool_call_json.startswith("{"):
                # Find the matching closing brace
                brace_count = 0
                end_index = 0
                for i, char in enumerate(tool_call_json):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end_index = i + 1
                            break
                
                tool_call_json = tool_call_json[:end_index]
                return json.loads(tool_call_json)
                
        except (json.JSONDecodeError, IndexError) as e:
            print(f"⚠️  Could not parse tool call: {e}")
            
        return None
    
    async def process_conversation_turn(self, session: ClientSession, user_message: str, 
                                      conversation_history: List[Dict[str, str]]) -> str:
        """
        Process a single conversation turn, potentially involving tool calls
        """
        max_iterations = 3  # Prevent infinite loops
        current_message = user_message
        
        for iteration in range(max_iterations):
            # Get LLM response
            llm_response = await self.get_llm_response(current_message, conversation_history)
            
            # Check if LLM wants to use a tool
            tool_call = self._extract_tool_call(llm_response)
            
            if tool_call is None:
                # No tool call, return the response
                return llm_response
            
            # Execute the tool
            try:
                tool_result = await self.execute_mcp_tool(
                    session,
                    tool_call["tool_name"],
                    tool_call["arguments"]
                )
                
                # Add tool result to conversation and continue
                conversation_history.extend([
                    {"role": "assistant", "content": llm_response},
                    {"role": "user", "content": f"Tool result: {tool_result}"}
                ])
                
                current_message = "Please provide a comprehensive answer based on the tool results above."
                
            except MCPToolError as e:
                return f"I encountered an error while querying the database: {e}"
        
        return "I'm having trouble completing this request after multiple attempts."
    
    async def chat_loop(self):
        """
        Main chat loop
        """
        print("\n" + "="*80)
        print("🚀 Blockchain Analytics Chatbot v3 (MCP + Groq)")
        print("   Ask questions about Ethereum consensus layer data!")
        print("   Type 'quit' to exit")
        print("="*80 + "\n")
        
        # Use proper async context manager pattern
        transport = await self.create_mcp_session()
        
        async with transport as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await self.initialize_session(session)
                
                conversation_history = []
                
                while True:
                    user_input = input("\n💬 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        print("👋 Goodbye!")
                        break
                    
                    if not user_input:
                        continue
                    
                    print("\n🤔 Thinking...")
                    
                    # Process the conversation turn
                    response = await self.process_conversation_turn(
                        session, user_input, conversation_history
                    )
                    
                    print(f"\n🤖 Assistant: {response}")
                    
                    # Add to conversation history
                    conversation_history.extend([
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": response}
                    ])
                    
                    # Keep conversation history manageable
                    if len(conversation_history) > 20:
                        conversation_history = conversation_history[-20:]


async def test_basic_functionality():
    """
    Test basic MCP connectivity and tool discovery
    """
    print("🧪 Testing basic MCP functionality...")
    
    chatbot = BlockchainChatbotMCPv3()
    
    try:
        # Use proper async context manager pattern
        transport = await chatbot.create_mcp_session()
        
        async with transport as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await chatbot.initialize_session(session)
                
                # Test basic queries
                test_queries = [
                    ("list_databases", {}),
                    ("list_tables", {"database": "goteth_mainnet"}),
                ]
                
                for tool_name, args in test_queries:
                    try:
                        result = await chatbot.execute_mcp_tool(session, tool_name, args)
                        print(f"✅ {tool_name}: Success")
                        print(f"   Result preview: {str(result)[:200]}...")
                    except Exception as e:
                        print(f"❌ {tool_name}: {e}")
                
                print("✅ Basic functionality test completed")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run basic functionality test
        asyncio.run(test_basic_functionality())
    else:
        # Run interactive chat
        chatbot = BlockchainChatbotMCPv3()
        asyncio.run(chatbot.chat_loop()) 