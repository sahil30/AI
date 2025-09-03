#!/usr/bin/env python3
"""
Example usage of the AI Integration Agent with Custom API
"""

import asyncio
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config
from agent import AIAgent
from integrations import CustomAPIIntegration

async def run_custom_api_examples():
    """Run example commands to demonstrate the AI agent with custom API."""
    try:
        # Ensure we're using custom API
        os.environ['USE_CUSTOM_API'] = 'true'
        config.use_custom_api = True
        
        # Validate config (will check for custom API variables)
        config.validate()
        
        agent = AIAgent()
        
        print("🤖 AI Agent Examples - Custom API Edition\n")
        print(f"Using API: {config.api.base_url}")
        print(f"API Version: {config.api.version}")
        print()

        # Example 1: Test API connection
        print("🔌 Example 1: Testing API Connection")
        try:
            result = await agent.process_command('Test the API connection')
            print("Connection Test Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Connection test failed: {e}")
        print("\n---\n")

        # Example 2: Get an issue/ticket
        print("🎫 Example 2: Getting Issue/Ticket")
        try:
            result = await agent.process_command('Get issue TICKET-123')
            print("Issue Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Get issue failed: {e}")
        print("\n---\n")

        # Example 3: Search for issues
        print("🔍 Example 3: Searching Issues")
        try:
            result = await agent.process_command('Search for open tickets in project DEMO')
            print("Search Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Search failed: {e}")
        print("\n---\n")

        # Example 4: Create a new issue
        print("📝 Example 4: Creating New Issue")
        try:
            result = await agent.process_command('Create a new issue: "Fix login authentication bug"')
            print("Create Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Create issue failed: {e}")
        print("\n---\n")

        # Example 5: Direct custom API call
        print("🔧 Example 5: Direct Custom API Call")
        try:
            result = await agent.process_command('Make a GET request to /v1/projects endpoint')
            print("Direct API Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Direct API call failed: {e}")
        print("\n---\n")

        # Example 6: Get a documentation page
        print("📚 Example 6: Getting Documentation Page")
        try:
            result = await agent.process_command('Get page DOC-456')
            print("Page Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Get page failed: {e}")
        print("\n---\n")

        # Example 7: Search documentation
        print("🔎 Example 7: Searching Documentation")
        try:
            result = await agent.process_command('Search documentation for "API authentication"')
            print("Documentation Search Result:", json.dumps(result, indent=2, default=str))
        except Exception as e:
            print(f"Documentation search failed: {e}")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 Make sure to:")
        print("1. Set USE_CUSTOM_API=true in your .env file")
        print("2. Configure API_BASE_URL and API_KEY")
        print("3. Ensure your custom API is accessible")
    except Exception as e:
        print(f"Example execution error: {e}")

def test_direct_custom_api():
    """Test direct custom API integration without AI layer."""
    print("\n🧪 Testing Direct Custom API Integration")
    
    try:
        # Ensure we're using custom API
        os.environ['USE_CUSTOM_API'] = 'true'
        config.use_custom_api = True
        config.validate()
        
        api = CustomAPIIntegration()
        
        print(f"API Base URL: {api.base_url}")
        print(f"API Version: {api.version}")
        
        # Test connection
        print("\n🔌 Testing Connection...")
        connection_result = api.test_connection()
        print("Connection Result:", json.dumps(connection_result, indent=2))
        
        # Get API info
        print("\n📊 Getting API Info...")
        api_info = api.get_api_info()
        print("API Info:", json.dumps(api_info, indent=2))
        
        # Test basic endpoints (these will likely fail with demo URLs, but show the structure)
        print("\n📋 Testing Issues Endpoint...")
        try:
            issues = api.search_issues(limit=5)
            print("Issues:", json.dumps(issues, indent=2)[:500] + "..." if len(str(issues)) > 500 else str(issues))
        except Exception as e:
            print(f"Issues endpoint test: {e}")
        
        print("\n📚 Testing Pages Endpoint...")
        try:
            pages = api.search_pages(limit=5)
            print("Pages:", json.dumps(pages, indent=2)[:500] + "..." if len(str(pages)) > 500 else str(pages))
        except Exception as e:
            print(f"Pages endpoint test: {e}")
        
        print("\n🏢 Testing Projects Endpoint...")
        try:
            projects = api.get_projects(limit=5)
            print("Projects:", json.dumps(projects, indent=2)[:500] + "..." if len(str(projects)) > 500 else str(projects))
        except Exception as e:
            print(f"Projects endpoint test: {e}")
        
    except Exception as e:
        print(f"Direct API test error: {e}")

def show_custom_api_configuration():
    """Show how to configure the custom API endpoints."""
    print("\n⚙️  Custom API Configuration Guide")
    print("="*50)
    
    print("\n1. Environment Variables (.env file):")
    print("""
API_BASE_URL=https://your-api-domain.com
API_KEY=your-api-key-here
API_VERSION=v1
USE_CUSTOM_API=true
OPENAI_API_KEY=your-openai-key
""")
    
    print("\n2. Default Endpoint Mapping:")
    print("""
Issues/Tickets:
  - List:   GET /v1/issues
  - Get:    GET /v1/issues/{id}
  - Create: POST /v1/issues
  - Update: PUT /v1/issues/{id}
  - Search: GET /v1/issues/search
  - Comments: GET/POST /v1/issues/{id}/comments

Pages/Documentation:
  - List:   GET /v1/pages
  - Get:    GET /v1/pages/{id}
  - Create: POST /v1/pages
  - Update: PUT /v1/pages/{id}
  - Search: GET /v1/pages/search
  - Spaces: GET /v1/spaces

Projects:
  - List:   GET /v1/projects
  - Get:    GET /v1/projects/{id}
""")
    
    print("\n3. Customizing Endpoints (Python code):")
    print("""
from integrations import CustomAPIIntegration

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
""")
    
    print("\n4. Authentication:")
    print("- Uses Bearer token authentication")
    print("- Token sent in Authorization header: 'Bearer {your-api-key}'")
    
    print("\n5. Expected Response Formats:")
    print("""
Issues should return fields like: id, title/summary, description, status, assignee
Pages should return fields like: id, title/name, content/body, space
Projects should return fields like: id, key/code, name, description
""")

if __name__ == "__main__":
    print("🤖 AI Integration Agent - Custom API Examples")
    print("=" * 60)
    
    # Show configuration guide first
    show_custom_api_configuration()
    
    # Run direct API tests
    test_direct_custom_api()
    
    # Run AI agent examples
    asyncio.run(run_custom_api_examples())