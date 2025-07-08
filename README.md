# Blockchain Analytics Chatbot

A natural language interface for querying Ethereum consensus layer blockchain data through conversational AI.

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.9.4-green.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Ask questions in natural language and get intelligent responses from 200M+ Ethereum consensus layer records:

```
You: "How many validators are currently active?"

Assistant: "Based on the latest data, there are approximately 
1.98 million active validators securing the Ethereum network, 
representing a robust and highly decentralized consensus mechanism."
```

## Features

- **Natural Language Processing**: Ask complex blockchain questions in plain English
- **Real-time Data**: Query live Ethereum consensus layer data (200M+ records)
- **Intelligent SQL Generation**: Automatic translation of questions to optimized ClickHouse queries
- **Multi-turn Conversations**: Context-aware dialogue with follow-up questions
- **Production Ready**: Robust error handling and async architecture

## Supported Data

- **Validators**: Status, balances, performance metrics (1.98M validators)
- **Blocks**: Production data, attestations, proposer information (11.96M records)
- **Staking Pools**: Performance analysis and rewards tracking (65.6M records)
- **Network Metrics**: Epoch summaries, participation rates (375K records)
- **Economic Data**: Rewards, fees, EIP-1559 burn data (7.6M records)

## Architecture

```
User Query → Groq LLM → MCP Tools → ClickHouse DB → Ethereum Data
     ↑                                                        ↓
Natural Language Response ← Result Processing ← Query Results
```

**Technology Stack:**
- **LLM**: Groq API (llama-3.1-70b-versatile)
- **Protocol**: Model Context Protocol (MCP) with official Python SDK
- **Database**: ClickHouse with SSH tunnel connectivity
- **Language**: Python 3.12+ with async/await

## Quick Start

### Prerequisites

- Python 3.12+
- SSH access to ClickHouse server
- Groq API key

### Installation

```bash
# Clone repository
git clone <repository-url>
cd blockchain-chatbot-mcp

# Setup environment
python3 -m venv mcp-env
source mcp-env/bin/activate  # Linux/Mac
pip install mcp-clickhouse clickhouse-connect groq python-dotenv

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### Configuration

Create `.env` file:

```bash
# ClickHouse Database
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8135
CLICKHOUSE_USER=mcp_reader
CLICKHOUSE_PASSWORD=your_password
CLICKHOUSE_DATABASE=goteth_mainnet
CLICKHOUSE_SECURE=false

# Groq LLM
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.1-70b-versatile
```

### Setup SSH Tunnel

```bash
# In separate terminal (keep running)
ssh -N -L 8135:localhost:8135 your_server@your_host
```

### Run

```bash
# Test connection
python blockchain_chatbot_mcp_v3.py test

# Start interactive chat
python blockchain_chatbot_mcp_v3.py
```

## Usage Examples

### Basic Queries
```
"How many validators are currently active?"
"What's the total amount of ETH staked?"
"Show me the latest epoch metrics"
```

### Advanced Analytics
```
"What was the validator participation rate in the last 10 epochs?"
"Which staking pools have the highest rewards?"
"Compare validator performance between epochs 375300 and 375310"
```

### Economic Analysis
```
"How much ETH was burned through EIP-1559 recently?"
"What were the highest block rewards this week?"
"Show me staking pool performance trends"
```

## Testing

```bash
# Basic connectivity test
python blockchain_chatbot_mcp_v3.py test

# Full integration test
python test_chatbot_integration.py
```

## Project Structure

```
blockchain-chatbot-mcp/
├── blockchain_chatbot_mcp_v3.py          # Main implementation
├── test_chatbot_integration.py           # Integration tests
├── COMPREHENSIVE_PROJECT_DOCUMENTATION.md # Complete technical docs
├── README.md                             # This file
├── .env.example                          # Environment template
└── mcp-env/                              # Python virtual environment
```

## Development Status

### Phase 1: MCP Server Infrastructure (Complete)
- ClickHouse database connectivity
- MCP server setup and tool discovery
- SSH tunnel configuration
- Schema mapping and validation

### Phase 2: LLM Integration (Complete)  
- Groq API integration
- Natural language processing
- Custom tool calling protocol
- Multi-turn conversation support

### Phase 3: Enhanced Analytics & UI (Planned)
- Web interface development
- Advanced multi-table analytics
- Query result caching
- Data visualization

### Phase 4: Production Deployment (Planned)
- Docker containerization
- Authentication & authorization
- Monitoring & logging
- Horizontal scaling

### Phase 5: OVH AI Migration (Planned)
- Migration to OVH AI Endpoints
- Custom model fine-tuning
- European data residency
- Cost optimization

##  Architecture Decisions

### Why This Approach Succeeded

After multiple failed attempts with:
-  LangChain community integrations
-  Custom MCP bridges  
-  Direct JSON-RPC implementations
-  JavaScript approaches

We succeeded with:
-  **Official Python MCP SDK**: Proper protocol compliance
-  **Async Context Management**: Reliable resource handling
-  **Custom Tool Calling**: Bridge between LLM and MCP protocols
-  **Schema Intelligence**: Embedded blockchain domain knowledge

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## Troubleshooting

### Common Issues

**SSH Tunnel**: `Connection refused`
```bash
ssh -N -L 8135:localhost:8135 your_server@your_host
```

**MCP Errors**: `Unexpected keyword argument`
- Check tool signatures in logs
- Verify database connectivity

**API Issues**: `Authentication failed`
```bash
echo $GROQ_API_KEY  # Verify API key is set
```

See [Troubleshooting Guide](COMPREHENSIVE_PROJECT_DOCUMENTATION.md#troubleshooting) for detailed solutions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.



