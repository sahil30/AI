#!/usr/bin/env python3
"""
Example usage of the AI Agent with MCP server integration.

This example shows how to use the AI agent with MCP (Model Context Protocol) servers
for Jira and Confluence integration, providing seamless Claude Desktop compatibility.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.ai_agent import AIAgent


async def main():
    """Main example function demonstrating MCP integration."""
    
    # Create and start the AI agent with MCP servers
    async with AIAgent() as agent:
        print("🚀 AI Agent with MCP servers started successfully!")
        
        # Example 1: Get a Jira issue
        print("\n📋 Example 1: Getting a Jira issue")
        try:
            result = await agent.process_command("Get Jira issue DEMO-123")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 2: Search for issues
        print("\n🔍 Example 2: Searching for Jira issues")
        try:
            result = await agent.process_command("Search for all open bugs in project DEMO")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 3: Get a Confluence page
        print("\n📄 Example 3: Getting a Confluence page")
        try:
            result = await agent.process_command("Get Confluence page 12345")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 4: Search Confluence content
        print("\n📚 Example 4: Searching Confluence content")
        try:
            result = await agent.process_command("Search Confluence for pages about API documentation")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 5: Create a new Jira issue
        print("\n✨ Example 5: Creating a new Jira issue")
        try:
            result = await agent.process_command(
                "Create a new bug in project DEMO with title 'Login page not loading' "
                "and description 'Users report 500 error when trying to log in'"
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 6: Create a Confluence page
        print("\n📝 Example 6: Creating a Confluence page")
        try:
            result = await agent.process_command(
                "Create a page in DEV space with title 'API Integration Guide' "
                "and content about integrating with our REST API"
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 7: Analyze Java code
        print("\n☕ Example 7: Analyzing Java code")
        java_code = """
        public class Calculator {
            public int add(int a, int b) {
                return a + b;
            }
            
            public int multiply(int a, int b) {
                return a * b;
            }
        }
        """
        try:
            result = await agent.process_command(f"Analyze this Java code: {java_code}")
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
        
        # Example 8: Complex workflow - Create issue and documentation
        print("\n🔄 Example 8: Complex workflow")
        try:
            result = await agent.process_command(
                "Create a new task in DEMO project called 'Implement user authentication' "
                "and then create a Confluence page in DEV space documenting the implementation plan"
            )
            print(f"Result: {result}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n✅ MCP integration examples completed!")


def check_environment():
    """Check if the environment is properly configured for MCP usage."""
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please check your .env file configuration.")
        return False
    
    # Check if MCP servers are configured
    if os.getenv('USE_MCP_SERVERS', 'false').lower() == 'true':
        mcp_vars = ['MCP_JIRA_SERVER_PATH', 'MCP_CONFLUENCE_SERVER_PATH']
        missing_mcp = [var for var in mcp_vars if not os.getenv(var)]
        
        if missing_mcp:
            print(f"⚠️  MCP servers enabled but missing paths: {', '.join(missing_mcp)}")
            print("Make sure your MCP server paths are correctly configured.")
    
    return True


if __name__ == "__main__":
    print("🤖 AI Agent MCP Integration Example")
    print("=" * 50)
    
    if not check_environment():
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)