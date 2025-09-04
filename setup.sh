#!/bin/bash

# AI Agent Setup Script
# This script helps set up the AI Integration Agent with different configuration options

set -e

echo "🤖 AI Integration Agent Setup"
echo "============================"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+' || echo "0.0")
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.12+ is required. Found: Python $python_version"
    echo "Please install Python 3.12 or higher."
    exit 1
fi

echo "✅ Python version check passed: $python_version"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env with your configuration!"
    echo "   - Add your OpenAI API key"
    echo "   - Choose your integration method (MCP/Custom API/Atlassian)"
    echo "   - Add your API credentials"
    echo ""
else
    echo "ℹ️  .env file already exists"
    echo ""
fi

# Setup options
echo "🚀 Choose your setup option:"
echo ""
echo "1) MCP Servers (Recommended for Claude Desktop)"
echo "   - Use dedicated MCP servers for Jira and Confluence"
echo "   - Best integration with Claude Desktop"
echo "   - Requires setting up MCP servers separately"
echo ""
echo "2) Custom API"
echo "   - Use your own API endpoints"
echo "   - Direct integration with custom backend"
echo "   - Configure API_BASE_URL and API_KEY"
echo ""
echo "3) Standard Atlassian APIs"
echo "   - Direct integration with Jira and Confluence"
echo "   - Requires Atlassian API tokens"
echo "   - Traditional setup method"
echo ""
echo "4) Skip configuration (manual setup)"
echo ""

read -p "Select option (1-4): " option

case $option in
    1)
        echo ""
        echo "🔧 Setting up for MCP servers..."
        echo ""
        echo "USE_MCP_SERVERS=true" >> .env
        echo "USE_CUSTOM_API=false" >> .env
        echo ""
        echo "✅ MCP server configuration added to .env"
        echo ""
        echo "📋 Next steps:"
        echo "1. Set up your MCP servers (mcp-jira-python and mcp-confluence-python)"
        echo "2. Update MCP_JIRA_SERVER_PATH and MCP_CONFLUENCE_SERVER_PATH in .env"
        echo "3. Add your OPENAI_API_KEY to .env"
        echo "4. Run: python examples/mcp_usage_example.py"
        ;;
    2)
        echo ""
        echo "🔧 Setting up for Custom API..."
        echo ""
        echo "USE_MCP_SERVERS=false" >> .env
        echo "USE_CUSTOM_API=true" >> .env
        echo ""
        read -p "Enter your API base URL: " api_url
        read -p "Enter your API key: " api_key
        read -p "Enter API version (default: v1): " api_version
        api_version=${api_version:-v1}
        
        echo "API_BASE_URL=$api_url" >> .env
        echo "API_KEY=$api_key" >> .env
        echo "API_VERSION=$api_version" >> .env
        echo ""
        echo "✅ Custom API configuration added to .env"
        echo ""
        echo "📋 Next steps:"
        echo "1. Add your OPENAI_API_KEY to .env"
        echo "2. Run: python examples/custom_api_usage.py"
        ;;
    3)
        echo ""
        echo "🔧 Setting up for Atlassian APIs..."
        echo ""
        echo "USE_MCP_SERVERS=false" >> .env
        echo "USE_CUSTOM_API=false" >> .env
        echo ""
        echo "✅ Atlassian API configuration set"
        echo ""
        echo "📋 Next steps:"
        echo "1. Add your Jira and Confluence credentials to .env"
        echo "2. Add your OPENAI_API_KEY to .env"
        echo "3. Run: python examples/example_usage.py"
        ;;
    4)
        echo ""
        echo "⚙️  Manual setup selected"
        echo ""
        echo "📋 Next steps:"
        echo "1. Edit .env file with your configuration"
        echo "2. Choose your integration method"
        echo "3. Add your API credentials"
        echo "4. Run the appropriate example script"
        ;;
    *)
        echo "❌ Invalid option selected"
        exit 1
        ;;
esac

echo ""
echo "🎯 Quick Test Commands:"
echo ""
echo "# Validate configuration"
echo "python -m src.main validate-config"
echo ""
echo "# Interactive mode"
echo "python -m src.main interactive"
echo ""
echo "# Test API connection"
echo "python -m src.main execute \"Test the API connection\""
echo ""

# Check if OpenAI API key is set
if ! grep -q "OPENAI_API_KEY=your-openai-api-key" .env; then
    echo "✅ Setup complete!"
else
    echo "⚠️  Don't forget to add your OPENAI_API_KEY to the .env file!"
fi

echo ""
echo "📚 For detailed instructions, see HOW_TO_RUN.md"
echo "🚀 Happy coding!"