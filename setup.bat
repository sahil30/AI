@echo off
REM AI Agent Setup Script for Windows
REM This script helps set up the AI Integration Agent with different configuration options

echo 🤖 AI Integration Agent Setup
echo ============================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.12 or higher.
    pause
    exit /b 1
)

echo ✅ Python check passed
echo.

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error installing dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed
echo.

REM Check if .env exists
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env >nul
    echo ✅ Created .env file
    echo.
    echo ⚠️  IMPORTANT: You need to edit .env with your configuration!
    echo    - Add your OpenAI API key
    echo    - Choose your integration method (MCP/Custom API/Atlassian)
    echo    - Add your API credentials
    echo.
) else (
    echo ℹ️  .env file already exists
    echo.
)

REM Setup options
echo 🚀 Choose your setup option:
echo.
echo 1^) MCP Servers (Recommended for Claude Desktop^)
echo    - Use dedicated MCP servers for Jira and Confluence
echo    - Best integration with Claude Desktop
echo    - Requires setting up MCP servers separately
echo.
echo 2^) Custom API
echo    - Use your own API endpoints
echo    - Direct integration with custom backend
echo    - Configure API_BASE_URL and API_KEY
echo.
echo 3^) Standard Atlassian APIs
echo    - Direct integration with Jira and Confluence
echo    - Requires Atlassian API tokens
echo    - Traditional setup method
echo.
echo 4^) Skip configuration (manual setup^)
echo.

set /p option="Select option (1-4): "

if "%option%"=="1" (
    echo.
    echo 🔧 Setting up for MCP servers...
    echo.
    echo USE_MCP_SERVERS=true >> .env
    echo USE_CUSTOM_API=false >> .env
    echo.
    echo ✅ MCP server configuration added to .env
    echo.
    echo 📋 Next steps:
    echo 1. Set up your MCP servers (mcp-jira-python and mcp-confluence-python^)
    echo 2. Update MCP_JIRA_SERVER_PATH and MCP_CONFLUENCE_SERVER_PATH in .env
    echo 3. Add your OPENAI_API_KEY to .env
    echo 4. Run: python examples/mcp_usage_example.py
) else if "%option%"=="2" (
    echo.
    echo 🔧 Setting up for Custom API...
    echo.
    echo USE_MCP_SERVERS=false >> .env
    echo USE_CUSTOM_API=true >> .env
    echo.
    set /p api_url="Enter your API base URL: "
    set /p api_key="Enter your API key: "
    set /p api_version="Enter API version (default: v1): "
    if "%api_version%"=="" set api_version=v1
    
    echo API_BASE_URL=%api_url% >> .env
    echo API_KEY=%api_key% >> .env
    echo API_VERSION=%api_version% >> .env
    echo.
    echo ✅ Custom API configuration added to .env
    echo.
    echo 📋 Next steps:
    echo 1. Add your OPENAI_API_KEY to .env
    echo 2. Run: python examples/custom_api_usage.py
) else if "%option%"=="3" (
    echo.
    echo 🔧 Setting up for Atlassian APIs...
    echo.
    echo USE_MCP_SERVERS=false >> .env
    echo USE_CUSTOM_API=false >> .env
    echo.
    echo ✅ Atlassian API configuration set
    echo.
    echo 📋 Next steps:
    echo 1. Add your Jira and Confluence credentials to .env
    echo 2. Add your OPENAI_API_KEY to .env
    echo 3. Run: python examples/example_usage.py
) else if "%option%"=="4" (
    echo.
    echo ⚙️  Manual setup selected
    echo.
    echo 📋 Next steps:
    echo 1. Edit .env file with your configuration
    echo 2. Choose your integration method
    echo 3. Add your API credentials
    echo 4. Run the appropriate example script
) else (
    echo ❌ Invalid option selected
    pause
    exit /b 1
)

echo.
echo 🎯 Quick Test Commands:
echo.
echo # Validate configuration
echo python -m src.main validate-config
echo.
echo # Interactive mode
echo python -m src.main interactive
echo.
echo # Test API connection
echo python -m src.main execute "Test the API connection"
echo.

REM Check if OpenAI API key is set
findstr /C:"OPENAI_API_KEY=your-openai-api-key" .env >nul
if not errorlevel 1 (
    echo ⚠️  Don't forget to add your OPENAI_API_KEY to the .env file!
) else (
    echo ✅ Setup complete!
)

echo.
echo 📚 For detailed instructions, see HOW_TO_RUN.md
echo 🚀 Happy coding!
echo.
pause