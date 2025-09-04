# How to Run the AI Agent

This guide shows you how to set up and run the AI Integration Agent with different configuration options.

## 📋 Prerequisites

- **Python 3.12+** installed on your system
- **OpenAI API key** (required for all configurations)
- One of the following:
  - MCP servers set up (Option 1)
  - Custom API access (Option 2)  
  - Atlassian API access (Option 3)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd ai-agent-python
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration (see options below)
```

### 3. Choose Your Integration Method

## Option 1: MCP Servers (Recommended for Claude Desktop)

### Setup MCP Servers First

Make sure your MCP servers are set up:

```bash
# Set up Jira MCP server
cd ../mcp-jira-python
pip install -r requirements.txt
cp .env.example .env
# Edit mcp-jira-python/.env with your Jira credentials

# Set up Confluence MCP server  
cd ../mcp-confluence-python
pip install -r requirements.txt
cp .env.example .env
# Edit mcp-confluence-python/.env with your Confluence credentials
```

### Configure AI Agent for MCP

Edit `ai-agent-python/.env`:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your-openai-api-key

# MCP Server Configuration
USE_MCP_SERVERS=true
MCP_JIRA_SERVER_PATH=/absolute/path/to/mcp-jira-python
MCP_CONFLUENCE_SERVER_PATH=/absolute/path/to/mcp-confluence-python

# Agent Configuration
LOG_LEVEL=INFO
```

### Run with MCP Servers

```bash
# Interactive mode
python -m src.main interactive

# Run MCP example
python examples/mcp_usage_example.py

# Single command
python -m src.main execute "Get issue DEMO-123"
```

## Option 2: Custom API Integration

### Configure for Custom API

Edit `ai-agent-python/.env`:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your-openai-api-key

# Custom API Configuration
USE_MCP_SERVERS=false
USE_CUSTOM_API=true
API_BASE_URL=https://your-api-domain.com
API_KEY=your-custom-api-key
API_VERSION=v1

# Agent Configuration
LOG_LEVEL=INFO
```

### Run with Custom API

```bash
# Interactive mode
python -m src.main interactive

# Test connection
python -m src.main execute "Test the API connection"

# Run custom API example
python examples/custom_api_usage.py
```

## Option 3: Standard Atlassian APIs

### Configure for Atlassian APIs

Edit `ai-agent-python/.env`:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your-openai-api-key

# Disable other options
USE_MCP_SERVERS=false
USE_CUSTOM_API=false

# Jira Configuration
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token

# Confluence Configuration
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-confluence-api-token

# Agent Configuration
LOG_LEVEL=INFO
```

### Run with Atlassian APIs

```bash
# Interactive mode
python -m src.main interactive

# Run standard example
python examples/example_usage.py

# Validate configuration
python -m src.main validate-config
```

## 🎯 Running Examples

### Interactive Mode

Start an interactive shell to chat with the AI agent:

```bash
python -m src.main interactive
```

Example session:
```
🤖 AI Agent Interactive Mode
Type 'help' for commands, 'quit' to exit.

AI Agent> Get issue DEMO-123
[Agent fetches and displays issue details]

AI Agent> Create page in DEV space: API Documentation
[Agent creates a new Confluence page]

AI Agent> Analyze this Java code: public class Test { ... }
[Agent analyzes the Java code]

AI Agent> quit
Goodbye! 👋
```

### Command Line Usage

Execute single commands directly:

```bash
# Get a specific issue
python -m src.main execute "Get issue PROJ-123"

# Search with context
python -m src.main execute "Search issues" --context '{"project": "DEMO"}'

# Generate documentation from Jira issue
python -m src.main doc-from-issue PROJ-123 DEVSPACE

# Analyze Java project
python -m src.main analyze-java /path/to/java/project --output analysis.json

# Test API connection
python -m src.main execute "Test the API connection"
```

### Python Script Usage

Create your own Python scripts:

```python
import asyncio
from src.agent import AIAgent

async def main():
    async with AIAgent() as agent:
        # Process natural language commands
        result = await agent.process_command("Get issue DEMO-1")
        print(result)
        
        # Create documentation from issue
        doc_result = await agent.process_command(
            "Create documentation for issue DEMO-1 in DOCS space"
        )
        print(doc_result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Example Commands

### Jira Commands
```bash
"Get issue DEMO-123"
"Search for all open bugs in project MYPROJ"
"Create a new task in DEMO: Update documentation"
"Add comment to DEMO-123: Working on this issue"
"Show me all projects"
"What are the available transitions for DEMO-123?"
```

### Confluence Commands
```bash
"Get page 12345"
"Search for pages about API authentication"
"Create a page in DEV space with title 'New API Guide'"
"Show me all spaces"
"Get child pages of page 67890"
"Add a comment to page 12345 about the recent updates"
```

### Java Code Commands
```bash
"Analyze this Java code: [paste code here]"
"Generate a UserService class with CRUD operations"
"Analyze Java project /path/to/my/project"
"Create a Calculator class with basic math operations"
```

### Combined Workflows
```bash
"Get issue DEMO-123 and create a Confluence page documenting the solution"
"Search for all high priority bugs and create a summary page in DOCS space"
"Analyze this Java code and create an issue if there are problems"
```

## 🛠 Troubleshooting

### Configuration Issues

**Check your configuration:**
```bash
python -m src.main validate-config
```

**Common configuration errors:**
- Missing `OPENAI_API_KEY`
- Wrong MCP server paths (must be absolute paths)
- Invalid API credentials
- Wrong base URLs (check for trailing slashes)

### MCP Server Issues

**Test MCP servers individually:**
```bash
# Test Jira MCP server
cd mcp-jira-python
python -m mcp_jira_server.server

# Test Confluence MCP server
cd mcp-confluence-python  
python -m mcp_confluence_server.server
```

**Check MCP server logs:**
- Set `LOG_LEVEL=DEBUG` in MCP server `.env` files
- Check server startup messages
- Verify API credentials in MCP server configurations

### API Connection Issues

**Test API connectivity:**
```bash
python -m src.main execute "Test the API connection"
```

**Common API issues:**
- Network connectivity problems
- Invalid API tokens/credentials
- Insufficient API permissions
- Wrong base URLs or endpoints

### Python Environment Issues

**Check Python version:**
```bash
python --version  # Should be 3.12+
```

**Reinstall dependencies:**
```bash
pip install --upgrade -r requirements.txt
```

**Use virtual environment (recommended):**
```bash
python -m venv ai-agent-env
source ai-agent-env/bin/activate  # On Windows: ai-agent-env\Scripts\activate
pip install -r requirements.txt
```

## 🔧 Advanced Usage

### Custom Configuration

You can override configuration in code:

```python
import os
from src.agent import AIAgent

# Override environment variables
os.environ['USE_MCP_SERVERS'] = 'true'
os.environ['MCP_JIRA_SERVER_PATH'] = '/custom/path/to/mcp-jira-python'

async with AIAgent() as agent:
    result = await agent.process_command("Get issue DEMO-1")
```

### Multiple Environments

Create different `.env` files for different environments:

```bash
# Development
cp .env.example .env.dev
# Edit .env.dev

# Production  
cp .env.example .env.prod
# Edit .env.prod

# Load specific environment
python -c "from dotenv import load_dotenv; load_dotenv('.env.dev')" && python examples/mcp_usage_example.py
```

### Logging Configuration

Set detailed logging:

```bash
# In .env file
LOG_LEVEL=DEBUG

# Or set environment variable
export LOG_LEVEL=DEBUG
python -m src.main interactive
```

## 📚 Next Steps

1. **Explore Examples**: Check the `examples/` directory for more usage patterns
2. **Customize Integration**: Modify integrations in `src/integrations/`
3. **Add New Commands**: Extend the AI agent with custom functions
4. **Claude Desktop**: Use MCP servers with Claude Desktop for seamless integration

## 🆘 Getting Help

1. Check the **Troubleshooting** section above
2. Review the **README.md** for detailed API documentation
3. Test with provided example scripts
4. Check server logs for error messages
5. Verify all prerequisites are installed

Happy coding! 🚀