# Blockchain Analytics Chatbot - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Phase 1: MCP Server Infrastructure](#phase-1-mcp-server-infrastructure)
4. [Phase 2: LLM Integration](#phase-2-llm-integration)
5. [Technical Stack](#technical-stack)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [Testing & Validation](#testing--validation)
9. [Architecture Decisions](#architecture-decisions)
10. [Future Phases](#future-phases)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

**Objective**: Build a natural language interface for querying Ethereum consensus layer blockchain data through conversational AI.

**Core Capability**: Users can ask complex questions in natural language (e.g., "What was the validator participation rate in the last 10 epochs?") and receive accurate responses derived from real-time blockchain analytics data stored in a ClickHouse database.

**Current Status**: Phase 2 Complete ✅ - Production-ready natural language interface to Ethereum consensus layer data.

---

## System Architecture

### High-Level Architecture Flow
```
User Natural Language Query 
    ↓
Groq LLM Analysis & Intent Recognition
    ↓  
Custom Tool Call Protocol (TOOL_CALL: JSON)
    ↓
Official Python MCP SDK (ClientSession + stdio_client)
    ↓
MCP ClickHouse Server (mcp-clickhouse.main)
    ↓
SSH Tunnel → Remote ClickHouse Database
    ↓
Ethereum Consensus Layer Data (200M+ records, 28 tables)
    ↓
Result Processing & Natural Language Response
    ↓
User-Friendly Analytics Response
```

### Component Specifications

#### Database Layer (Phase 1 Foundation)
- **Technology**: ClickHouse 24.10.2.80
- **Data Scale**: Ethereum consensus layer analytics (200M+ records, 8GB)
- **Access Method**: Read-only via SSH tunnel
- **Tables**: 28 tables covering validators, blocks, rewards, network events
- **Connection**: SSH tunnel (localhost:8135 → remote:8135)

#### MCP Server Layer (Phase 1 Core)
- **Technology**: mcp-clickhouse Python package
- **Purpose**: Exposes database as standardized tools for LLM consumption
- **Tools Provided**:
  - `list_databases()`: Database discovery
  - `list_tables(database)`: Schema exploration  
  - `run_select_query(query)`: Query execution
- **Security**: Read-only mode, query timeouts, input validation

#### LLM Integration Layer (Phase 2 Core)
- **Technology**: Groq API with `llama-3.1-70b-versatile` model
- **Purpose**: Natural language understanding, SQL generation, result interpretation
- **Configuration**: Low temperature (0.1) for precise analytical queries
- **Tool Calling**: Custom protocol using JSON-formatted tool calls
- **Context Management**: Comprehensive database schema awareness

#### Communication Architecture (Phase 2 Innovation)
- **Protocol Bridge**: Custom tool calling format ↔ Official MCP JSON-RPC
- **Session Management**: Async context managers for resource cleanup
- **History Tracking**: Conversation state maintenance (up to 20 message limit)
- **Multi-turn Support**: Complex queries requiring multiple database interactions

---

## Phase 1: MCP Server Infrastructure

### Objective
Establish reliable connectivity between ClickHouse database and MCP (Model Context Protocol) server to expose blockchain data as standardized tools.

### Accomplished Components

#### 1. Environment Setup & Dependencies
```bash
# Core Dependencies
mcp-clickhouse: MCP server implementation for ClickHouse
clickhouse-connect: Database client library
python-dotenv: Environment configuration management

# Development Tools  
MCP Inspector: Browser-based MCP server testing interface
DBeaver: Database administration and query testing
SSH: Secure tunnel for database connectivity
```

#### 2. Network Infrastructure Configuration
```bash
# SSH Tunnel Configuration
ssh -N -L 8135:localhost:8135 jacobo@65.108.193.245

# Environment Variables
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8135
CLICKHOUSE_USER=mcp_reader
CLICKHOUSE_PASSWORD=password
CLICKHOUSE_DATABASE=goteth_mainnet
CLICKHOUSE_SECURE=false
CLICKHOUSE_VERIFY=false
```

#### 3. Database Schema Discovery
**Primary Database**: goteth_mainnet

**Scale**: 28 tables, ~200M records, 8GB storage  
**Engine**: Primarily ReplacingMergeTree for analytical workloads  
**Data Coverage**: Validators, blocks, rewards, network events, consensus metrics

**Key Tables**:
- `t_validator_last_status` (1.98M rows): Validator operational status
- `t_block_metrics` (11.96M rows): Block production analytics  
- `t_pool_summary` (65.6M rows): Staking pool performance
- `t_block_rewards` (7.6M rows): Economic incentive data
- `t_epoch_metrics_summary` (375K rows): Network health metrics

**Field Naming Convention**: All columns prefixed with `f_` (e.g., f_val_idx, f_epoch, f_balance_eth)

#### 4. Critical Issues Resolved

**Issue 1: SSL Configuration Mismatch**
- **Problem**: Initial HTTPS settings for SSH tunnel endpoint
- **Symptom**: SSLError during connection attempts
- **Resolution**: Set `CLICKHOUSE_SECURE=false` for HTTP-over-SSH-tunnel
- **Root Cause**: SSH tunnel provides encryption, local connection uses plain HTTP

**Issue 2: Database Account Restrictions**  
- **Problem**: mcp_reader account limited to 100 rows maximum
- **Symptom**: TOO_MANY_ROWS_OR_BYTES during client initialization
- **Resolution**: Administrator increased account limits to 10,000+ rows
- **Impact**: Blocked all operations until administrative intervention

### Phase 1 Validation Results
- ✅ MCP server initializes successfully
- ✅ Tool discovery works (3 tools discovered)
- ✅ Query execution returns valid blockchain data
- ✅ Result serialization maintains data integrity
- ✅ SSH tunnel maintains stable connectivity
- ✅ Error handling functions correctly

---

## Phase 2: LLM Integration

### Objective
Integrate Large Language Model capabilities with the established MCP server infrastructure to enable natural language querying of Ethereum consensus layer data.

### Accomplished Components

#### 1. Core Infrastructure Setup
```python
# Key Dependencies Added
groq: LLM API client for natural language processing  
Official MCP SDK: v1.9.4 with proper async patterns
JSON parsing: Custom tool call extraction and execution
```

#### 2. Main Implementation (`blockchain_chatbot_mcp_v3.py` - 412 lines)

**Class Architecture**:
- `BlockchainChatbotMCPv3`: Main chatbot implementation
- `DatabaseSchema`: Schema context management for LLM  
- `MCPToolError`: Custom exception handling for tool failures

**Key Methods**:
- `create_mcp_session()`: Establishes MCP connection using official SDK patterns
- `initialize_session()`: Tool discovery and session initialization
- `execute_mcp_tool()`: Safe tool execution with comprehensive error handling  
- `get_llm_response()`: Groq API integration with conversation history
- `process_conversation_turn()`: Complete conversation flow with tool calling
- `chat_loop()`: Interactive user interface

#### 3. Advanced Tool Calling Protocol
```
Format: TOOL_CALL: {"tool_name": "...", "arguments": {...}}
Parser: Custom JSON extraction with brace matching
Execution: Async tool execution with result integration
Context: Tool results fed back into LLM for comprehensive responses
```

#### 4. Database Schema Intelligence
- **Schema Context**: Embedded knowledge of 28 table structures
- **Query Optimization**: Automatic LIMIT clause insertion and aggregation suggestions
- **Field Mapping**: Complete understanding of `f_` prefixed column naming convention  
- **Temporal Context**: Awareness of current epoch ranges (~375000+)

#### 5. Validation Framework (`test_chatbot_integration.py` - 72 lines)
- **Integration Testing**: Full pipeline validation from user input to response
- **API Key Management**: Environment variable handling with fallback options
- **Tool Execution Testing**: Verification of MCP tool connectivity and execution
- **LLM Response Testing**: Groq API connectivity and response generation

### How Phase 2 Builds on Phase 1

#### 1. MCP Server Dependency
- **Phase 1 Foundation**: MCP server running with `python -m mcp_clickhouse.main`
- **Phase 2 Integration**: Uses `StdioServerParameters` to connect to existing server
- **Inheritance**: All 3 Phase 1 tools directly accessible through Phase 2 interface

#### 2. Database Schema Leverage  
- **Phase 1 Discovery**: 28 tables, field naming conventions, data types identified
- **Phase 2 Intelligence**: Schema knowledge embedded in LLM context for intelligent query generation
- **Query Optimization**: Automatic best practices (LIMIT clauses, aggregations) applied

#### 3. Connection Architecture
- **Phase 1 Infrastructure**: SSH tunnel, ClickHouse authentication, MCP tool interface
- **Phase 2 Layer**: Async session management wrapping Phase 1 connectivity  
- **Resource Management**: Proper cleanup of LLM sessions while maintaining database connections

### Phase 2 Validation Results
- ✅ Natural language query understanding
- ✅ Intelligent SQL generation based on user intent
- ✅ Multi-turn conversations with context retention
- ✅ Tool result interpretation and user-friendly explanations
- ✅ Complex analytical question decomposition
- ✅ End-to-end pipeline: User query → LLM → tool execution → ClickHouse → response

---

## Technical Stack

### Core Dependencies
```python
# LLM Integration
groq==0.x.x: Groq API client for natural language processing

# Official MCP SDK  
mcp==1.9.4: Official Python MCP SDK with proper async patterns

# Database Connectivity (from Phase 1)
mcp-clickhouse: MCP server implementation for ClickHouse
clickhouse-connect: Database client library

# Utilities
python-dotenv: Environment configuration management
asyncio: Async/await support for concurrent operations
```

### Infrastructure Requirements
- **Python**: 3.12+ runtime environment
- **Node.js**: MCP Inspector dependency (development only)
- **SSH Access**: Remote database connectivity
- **Virtual Environment**: Dependency isolation

### Network Architecture
- **Connection**: SSH tunnel (localhost:8135 → remote:8135)
- **Protocol**: HTTP over SSH tunnel (encryption at tunnel level)
- **Authentication**: Username/password with restricted permissions
- **API Access**: Groq API for LLM processing

---

## Installation & Setup

### Prerequisites
```bash
# System Requirements
Python 3.12+
SSH access to remote ClickHouse server
Groq API key

# Network Access
SSH tunnel capability
Internet access for Groq API
```

### Step 1: Environment Setup
```bash
# Clone repository (after git setup)
git clone <repository-url>
cd blockchain-chatbot-mcp

# Create virtual environment
python3 -m venv mcp-env
source mcp-env/bin/activate  # Linux/Mac
# or mcp-env\Scripts\activate  # Windows
```

### Step 2: Install Dependencies
```bash
# Install Python packages
pip install mcp-clickhouse clickhouse-connect groq python-dotenv

# Optional: Install MCP Inspector for development
npm install -g @modelcontextprotocol/inspector
```

### Step 3: Configure Environment
```bash
# Create .env file
cat > .env << EOF
# ClickHouse Configuration (Phase 1)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8135
CLICKHOUSE_USER=mcp_reader
CLICKHOUSE_PASSWORD=password
CLICKHOUSE_DATABASE=goteth_mainnet
CLICKHOUSE_SECURE=false
CLICKHOUSE_VERIFY=false

# Groq Configuration (Phase 2)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.1-70b-versatile
EOF
```

### Step 4: Establish SSH Tunnel
```bash
# In separate terminal (keep running)
ssh -N -L 8135:localhost:8135 jacobo@65.108.193.245
```

### Step 5: Verify Installation
```bash
# Test basic functionality
python blockchain_chatbot_mcp_v3.py test

# Expected output:
# 🧪 Testing basic MCP functionality...
# ✅ MCP connection established and initialized
# 🔧 Discovered 3 MCP tools...
# ✅ Basic functionality test completed
```

---

## Usage Guide

### Interactive Chat Mode
```bash
# Start the chatbot
source mcp-env/bin/activate
python blockchain_chatbot_mcp_v3.py
```

### Example Queries

#### Basic Queries
```
"How many validators are currently active?"
"What's the total amount of ETH staked?"
"Show me the latest epoch metrics"
```

#### Analytical Queries  
```
"What was the validator participation rate in the last 10 epochs?"
"Which staking pools have the highest rewards?"
"How many blocks were proposed in the last epoch?"
```

#### Complex Questions
```
"Compare validator performance between epochs 375300 and 375310"
"What's the trend in network staking over the past week?"
"Show me validators that joined recently"
```

### Expected Response Flow
1. **Understanding**: LLM analyzes natural language question
2. **Tool Selection**: Determines appropriate MCP tools to use
3. **Query Generation**: Creates ClickHouse-compatible SQL
4. **Execution**: Runs queries through MCP interface
5. **Interpretation**: Processes results and provides context
6. **Response**: Returns user-friendly explanation with insights

---

## Testing & Validation

### Basic Connectivity Test
```bash
python blockchain_chatbot_mcp_v3.py test
```
**Validates**: MCP connection, tool discovery, basic database queries

### Full Integration Test
```bash
python test_chatbot_integration.py  
```
**Validates**: Groq API, complete conversation flow, tool execution

### Manual Testing Scenarios
1. **Simple queries** → Single tool execution
2. **Complex analytics** → Multi-tool workflows  
3. **Error conditions** → Graceful failure handling
4. **Conversation flow** → Multi-turn context retention

### Performance Benchmarks
- **Simple queries**: 2-4 seconds (LLM + database)
- **Complex queries**: 5-10 seconds (multiple tools)
- **Error recovery**: <1 second (graceful degradation)

---

## Architecture Decisions

### Why Official MCP SDK Succeeded

#### ✅ **Successful Approach**: Official Python MCP SDK
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Proper async context management
async with stdio_client(params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(name, args)
```

**Success Factors**:
- Official protocol implementation (no bugs)
- Proper async context managers  
- Standard stdio transport
- Automatic resource cleanup
- Full MCP specification compliance

#### ❌ **Failed Approaches** 
1. **LangChain Community Integration**: Protocol mismatches, tool loading failures
2. **Custom MCP Bridges**: Async context complexity, protocol errors  
3. **Direct JSON-RPC Implementation**: Message ordering issues, handshake failures
4. **JavaScript Approaches**: Language/runtime mismatch with Python ecosystem

### Custom Tool Calling Protocol

**Design Decision**: Bridge between Groq LLM and MCP protocols
```python
# LLM Output Format (Our Custom Protocol)
TOOL_CALL: {"tool_name": "run_select_query", "arguments": {"query": "SELECT..."}}

# Translated to MCP Call (Official Protocol)  
await session.call_tool("run_select_query", {"query": "SELECT..."})
```

**Rationale**: Provides flexibility while maintaining MCP standard compliance

---

## Future Phases

### Phase 3: Enhanced Analytics & UI Development (PLANNED)

#### Objectives
- Advanced multi-table analytics capabilities
- Web interface for broader accessibility  
- Performance optimization and caching
- Enhanced visualization capabilities

#### Planned Components
1. **Advanced Query Engine**
   - Multi-table JOIN operations
   - Complex time-series analysis
   - Aggregated historical metrics
   - Custom analytical functions

2. **Web Interface Development**
   - React-based frontend
   - Real-time query visualization  
   - Interactive chart generation
   - Export capabilities (CSV, JSON, PDF)

3. **Performance Optimization**
   - Query result caching
   - Response streaming for large datasets
   - Connection pooling optimization
   - Database query optimization

4. **Enhanced User Experience**
   - Query suggestions and auto-completion
   - Historical query management
   - Saved analysis templates
   - Collaborative features

#### Technical Requirements
- **Frontend**: React, Chart.js/D3.js for visualizations
- **Backend**: FastAPI or Flask for web API
- **Caching**: Redis for query result caching
- **Database**: Query optimization and indexing

#### Estimated Timeline: 4-6 weeks

### Phase 4: Production Deployment & Scaling (PLANNED)

#### Objectives
- Production-ready deployment infrastructure
- Multi-user support with authentication
- Monitoring and logging systems
- Horizontal scaling capabilities

#### Planned Components
1. **Infrastructure Hardening**
   - Containerization (Docker)
   - Kubernetes deployment
   - Load balancing
   - Failover mechanisms

2. **Authentication & Authorization**
   - User management system
   - API key management
   - Role-based access control
   - Usage quotas and rate limiting

3. **Monitoring & Observability**
   - Comprehensive logging
   - Metrics collection (Prometheus)
   - Performance monitoring
   - Error tracking and alerting

4. **API Gateway & Services**
   - RESTful API design
   - GraphQL endpoint consideration
   - Webhook support
   - Third-party integrations

#### Technical Requirements
- **Deployment**: Docker, Kubernetes, nginx
- **Monitoring**: Prometheus, Grafana, ELK stack
- **Security**: OAuth2, JWT tokens, API gateways
- **Databases**: Connection pooling, read replicas

#### Estimated Timeline: 6-8 weeks

### Phase 5: OVH AI Endpoints Migration (PLANNED)

#### Objectives
- Migrate from Groq to OVH AI Endpoints
- Cost optimization for production usage
- European data residency compliance
- Custom model fine-tuning capabilities

#### Planned Components
1. **API Migration**
   - OVH AI Endpoints integration
   - API compatibility layer
   - Performance benchmarking
   - Cost analysis and optimization

2. **Model Optimization**
   - Custom model fine-tuning for blockchain domain
   - Specialized prompt engineering
   - Domain-specific vocabulary enhancement
   - Query optimization patterns

3. **Infrastructure Integration**
   - European data center deployment
   - Compliance with GDPR requirements
   - Reduced latency for European users
   - Cost-effective scaling

#### Technical Requirements
- **AI Platform**: OVH AI Endpoints
- **Model Training**: Custom fine-tuning pipeline
- **Compliance**: GDPR, data residency requirements
- **Performance**: Latency optimization

#### Estimated Timeline: 3-4 weeks

---

## Troubleshooting

### Common Issues & Solutions

#### 1. SSH Tunnel Connection Issues
**Symptoms**: Connection refused, timeout errors
**Solutions**:
```bash
# Check tunnel status
ps aux | grep ssh

# Restart tunnel
ssh -N -L 8135:localhost:8135 jacobo@65.108.193.245

# Test connectivity
telnet localhost 8135
```

#### 2. MCP Tool Execution Errors
**Symptoms**: "Unexpected keyword argument" errors
**Solutions**:
- Verify tool signatures in system prompt
- Check MCP server logs for parameter validation
- Ensure database connection is active

#### 3. Groq API Issues
**Symptoms**: Authentication errors, rate limits
**Solutions**:
```bash
# Verify API key
echo $GROQ_API_KEY

# Check API status
curl -H "Authorization: Bearer $GROQ_API_KEY" \
     https://api.groq.com/openai/v1/models
```

#### 4. Database Query Timeouts
**Symptoms**: Query execution timeouts
**Solutions**:
- Add appropriate LIMIT clauses
- Use aggregate functions for large datasets
- Check database connection stability

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=1
python blockchain_chatbot_mcp_v3.py

# Test individual components
python blockchain_chatbot_mcp_v3.py test
python test_chatbot_integration.py
```

---

## Contributing

### Development Workflow
1. Create feature branch from main
2. Implement changes with comprehensive testing
3. Update documentation as needed
4. Submit pull request with detailed description

### Code Standards
- Follow PEP 8 Python style guidelines
- Include comprehensive docstrings
- Add unit tests for new functionality
- Ensure async/await patterns are properly implemented

### Testing Requirements
- All new features must include tests
- Maintain >90% code coverage
- Integration tests for critical paths
- Performance benchmarks for query operations

---

**Project Status**: Phase 2 Complete ✅  
**Production Readiness**: HIGH - Full functionality validated and tested  
**Next Milestone**: Phase 3 - Enhanced Analytics & UI Development

This documentation provides a complete technical reference for the Blockchain Analytics Chatbot project, covering all implemented phases and future development roadmap. 