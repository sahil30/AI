# AI Integration Agent - Python 3.12+ Edition

An intelligent agent that integrates with issue tracking, documentation systems, and provides Java code analysis/generation capabilities using OpenAI. **Supports both standard Atlassian APIs and custom APIs.**

## Features

🎯 **Issue/Ticket Management (Adaptive)**
- Get, search, create, update issues/tickets
- Add comments and manage status transitions
- Access project information
- **Works with both Jira API and custom APIs**

📖 **Documentation/Wiki Management (Adaptive)**
- Read, create, update, delete pages/documents
- Search content and manage spaces/collections
- Add comments and handle content formats
- **Works with both Confluence API and custom APIs**

☕ **Java Code Processing**
- Analyze Java code structure and complexity
- Generate Java classes and methods
- Parse and extract code information
- Calculate cyclomatic complexity

🤖 **AI-Powered Natural Language Interface**
- Process commands in natural language
- Intelligent function routing with API adaptation
- Context-aware responses
- Automatic format translation between API types

🔌 **Flexible Integration Options**
- **MCP Server Integration**: Use dedicated MCP servers for Claude Desktop compatibility
- **Custom API Integration**: Use your own API endpoints  
- **Standard Atlassian**: Traditional Jira/Confluence integration
- **Automatic Adaptation**: Seamless switching between API types
- **Claude Desktop Ready**: First-class MCP protocol support

## Requirements

- Python 3.12+
- OpenAI API key
- **Option 1**: MCP servers for Claude Desktop integration
- **Option 2**: Your custom API (base URL + API key)
- **Option 3**: Atlassian API access (username + API tokens)

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy environment configuration:
```bash
cp .env.example .env
```

4. Edit `.env` with your credentials:

**Option 1: Using MCP Servers (Recommended for Claude Desktop)**
```bash
# MCP Server Configuration
USE_MCP_SERVERS=true
MCP_JIRA_SERVER_PATH=/absolute/path/to/mcp-jira-python
MCP_CONFLUENCE_SERVER_PATH=/absolute/path/to/mcp-confluence-python

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
```

**Option 2: Using Your Custom API**
```bash
# Custom API Configuration
USE_MCP_SERVERS=false
USE_CUSTOM_API=true
API_BASE_URL=https://your-api-domain.com
API_KEY=your-custom-api-key
API_VERSION=v1

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
```

**Option 3: Using Standard Atlassian APIs**
```bash
# Standard Atlassian Configuration
USE_MCP_SERVERS=false
USE_CUSTOM_API=false
JIRA_BASE_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@example.com
CONFLUENCE_API_TOKEN=your-confluence-api-token

# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
```

## Usage

### MCP Server Integration

When using MCP servers, the AI agent automatically manages server lifecycle:

```python
import asyncio
from src.agent import AIAgent

async def main():
    # Agent automatically starts/stops MCP servers
    async with AIAgent() as agent:
        result = await agent.process_command("Get issue DEMO-123")
        print(result)

asyncio.run(main())
```

Or run the MCP example:
```bash
python examples/mcp_usage_example.py
```

### Interactive Mode

Start the interactive shell:
```bash
python -m src.main interactive
```

Then use natural language commands (works with both API types):
```
AI Agent> Test the API connection
AI Agent> Get issue PROJ-123
AI Agent> Search issues: project = MYPROJ AND status = Open
AI Agent> Create page in SPACE: API Documentation with content about REST APIs
AI Agent> Analyze this Java code: [paste code here]
AI Agent> Generate a UserService class with CRUD operations
AI Agent> Make a GET request to /v1/projects endpoint  # Custom API only
```

### Command Line Usage

Execute single commands:
```bash
# Get a Jira issue
python -m src.main execute "Get issue PROJ-123"

# Search issues with context
python -m src.main execute "Search issues" --context '{"project": "DEMO"}'

# Generate documentation from Jira issue
python -m src.main doc-from-issue PROJ-123 DEVSPACE

# Analyze Java project
python -m src.main analyze-java /path/to/java/project --output analysis.json

# Validate configuration
python -m src.main validate-config
```

### Python API Usage

```python
import asyncio
from src.agent import AIAgent
from src.config import config
from src.integrations import CustomAPIIntegration

async def main():
    # Validate configuration (checks for either custom or Atlassian API config)
    config.validate()
    
    # Initialize agent (automatically detects API type)
    agent = AIAgent()
    
    # Process natural language commands
    result = await agent.process_command("Get issue DEMO-1")
    print(result)
    
    # Direct API usage - works with both API types
    issue = agent.jira.get_issue("DEMO-1")  # Adaptive integration
    analysis = agent.java_processor.analyze_java_code(java_code)
    
    # Custom API direct access (if using custom API)
    if config.use_custom_api:
        custom_result = agent.custom_api.get("/v1/custom-endpoint")

asyncio.run(main())
```

## Example Commands

### Jira Commands
- `"Get issue PROJ-123"` - Get specific issue details
- `"Search issues in project DEMO"` - Search issues by project
- `"Create issue in PROJ: Fix login bug"` - Create new issue
- `"Add comment to PROJ-123: Working on this"` - Add comment
- `"Search issues: assignee = currentUser() AND status = Open"` - Complex JQL query

### Confluence Commands
- `"Get page 12345"` - Get page by ID
- `"Search pages about authentication"` - Content search
- `"Create page in SPACE: API Guide"` - Create new page
- `"Search content: space = DEV AND type = page"` - CQL search

### Java Code Commands
- `"Analyze this Java code: [paste code]"` - Code analysis
- `"Generate a ProductService class"` - Class generation
- `"Analyze Java project /path/to/project"` - Project analysis

### Combined Operations
- `"Create documentation for issue PROJ-123 in DEVSPACE"` - Auto-generate docs from Jira

## API Reference

### Configuration

The agent uses environment variables for configuration. All required variables must be set:

- `JIRA_BASE_URL` - Your Atlassian domain
- `JIRA_USERNAME` - Email address
- `JIRA_API_TOKEN` - API token from Jira
- `CONFLUENCE_BASE_URL` - Confluence wiki URL
- `CONFLUENCE_USERNAME` - Email address  
- `CONFLUENCE_API_TOKEN` - API token from Confluence
- `OPENAI_API_KEY` - OpenAI API key

### Core Classes

#### AIAgent
Main orchestrator that coordinates all integrations and AI processing.

#### JiraIntegration
Handles all Jira API operations:
- `get_issue(issue_key)` - Get issue details
- `search_issues(jql, fields)` - Search with JQL
- `create_issue(project_key, issue_data)` - Create issue
- `add_comment(issue_key, comment)` - Add comment

#### ConfluenceIntegration  
Manages Confluence operations:
- `get_page(page_id)` - Get page content
- `search_content(cql)` - Search with CQL
- `create_page(space_key, title, content)` - Create page
- `update_page(page_id, title, content, version)` - Update page

#### JavaProcessor
Provides Java code analysis:
- `analyze_java_code(code, filename)` - Analyze code structure
- `generate_java_class(class_name, options)` - Generate class
- `find_java_files(directory)` - Find Java files
- `write_java_file(file_path, content)` - Write code to file

## Development

### Project Structure
```
ai-agent-python/
├── src/
│   ├── agent/           # AI agent core
│   ├── integrations/    # Jira, Confluence, Java processors  
│   ├── config.py        # Configuration management
│   └── main.py          # CLI entry point
├── examples/            # Usage examples
├── requirements.txt     # Dependencies
├── pyproject.toml       # Project metadata
└── README.md
```

### Adding New Features

1. Add integration in `src/integrations/`
2. Update `AIAgent` class with new functions
3. Add function definitions for OpenAI
4. Update CLI commands in `main.py`

### Error Handling

The agent includes comprehensive error handling:
- Configuration validation on startup
- API timeout and retry logic
- Detailed error messages with context
- Logging for debugging

## Troubleshooting

**Configuration Issues:**
- Run `python -m src.main validate-config` to check settings
- Ensure API tokens have proper permissions
- Verify URLs are accessible

**API Errors:**
- Check network connectivity
- Verify API credentials are current
- Review Jira/Confluence permissions

**Java Analysis Issues:**
- Ensure Java code is syntactically valid
- Check file encoding (UTF-8 expected)
- Verify file paths are accessible

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Custom API Configuration

### Default Endpoint Structure

When using custom APIs, the agent expects these endpoint patterns:

```
Issues/Tickets:
  GET    /v1/issues              # List issues
  GET    /v1/issues/{id}         # Get specific issue
  POST   /v1/issues              # Create issue
  PUT    /v1/issues/{id}         # Update issue
  GET    /v1/issues/search       # Search issues
  GET    /v1/issues/{id}/comments # Get comments
  POST   /v1/issues/{id}/comments # Add comment

Documentation/Pages:
  GET    /v1/pages               # List pages
  GET    /v1/pages/{id}          # Get specific page
  POST   /v1/pages               # Create page
  PUT    /v1/pages/{id}          # Update page
  GET    /v1/pages/search        # Search pages
  GET    /v1/spaces              # List spaces

Projects:
  GET    /v1/projects            # List projects
  GET    /v1/projects/{id}       # Get specific project
```

### Custom Endpoint Mapping

You can customize endpoint paths in your code:

```python
from src.integrations import CustomAPIIntegration

api = CustomAPIIntegration()
api.configure_endpoints({
    'issues': {
        'list': '/api/tickets',
        'get': '/api/tickets/{id}',
        'search': '/api/tickets/query'
    },
    'pages': {
        'list': '/api/documents',
        'get': '/api/documents/{id}'
    }
})
```

### Expected Response Formats

Your custom API should return data with these field patterns:

**Issues/Tickets:**
- `id`, `key`, or `number` - Unique identifier
- `title`, `summary`, or `name` - Issue title
- `description`, `body`, or `content` - Issue details
- `status`, `state` - Current status
- `assignee`, `assigned_to` - Person assigned

**Pages/Documents:**
- `id` or `page_id` - Unique identifier  
- `title` or `name` - Page title
- `content`, `body`, or `text` - Page content
- `space`, `space_key` - Container/namespace

**Authentication:**
- Uses Bearer token: `Authorization: Bearer {your-api-key}`
- Configurable via `API_KEY` environment variable

### Migration from Atlassian APIs

The agent automatically translates between Atlassian and custom API formats, so you can use the same commands regardless of backend API type.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review example usage in `examples/` folder
3. Test with `examples/custom_api_usage.py` for custom APIs
4. Open an issue on the project repository