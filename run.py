#!/usr/bin/env python3
"""
Quick run script for the AI Integration Agent.
Provides easy access to common operations.
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.agent.ai_agent import AIAgent
from src.config import config


def print_banner():
    """Print the application banner."""
    print("🤖 AI Integration Agent")
    print("=" * 50)
    print()


async def interactive_mode():
    """Run the agent in interactive mode."""
    print_banner()
    print("Starting interactive mode...")
    print("Type 'help' for commands, 'quit' to exit.")
    print()
    
    async with AIAgent() as agent:
        while True:
            try:
                command = input("AI Agent> ").strip()
                
                if not command:
                    continue
                    
                if command.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                    
                if command.lower() == 'help':
                    show_help()
                    continue
                
                print(f"Processing: {command}")
                result = await agent.process_command(command)
                print(f"Result: {result}")
                print()
                
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")
                print()


def show_help():
    """Show help information."""
    print()
    print("📋 Available Commands:")
    print()
    print("Jira Commands:")
    print('  "Get issue DEMO-123"')
    print('  "Search for bugs in project MYPROJ"')
    print('  "Create task in DEMO: Fix login issue"')
    print('  "Add comment to DEMO-123: Working on this"')
    print()
    print("Confluence Commands:")
    print('  "Get page 12345"')
    print('  "Search pages about API documentation"')
    print('  "Create page in DEV: API Guide"')
    print()
    print("Java Commands:")
    print('  "Analyze this Java code: [paste code]"')
    print('  "Generate a Calculator class"')
    print()
    print("System Commands:")
    print('  "Test the API connection"')
    print('  help - Show this help')
    print('  quit - Exit the program')
    print()


async def execute_command(command, context=None):
    """Execute a single command."""
    print_banner()
    print(f"Executing: {command}")
    if context:
        print(f"Context: {context}")
    print()
    
    try:
        async with AIAgent() as agent:
            result = await agent.process_command(command, context)
            print("✅ Result:")
            print(result)
            return result
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def test_connection():
    """Test API connection."""
    print_banner()
    print("Testing API connection...")
    print()
    
    async def _test():
        async with AIAgent() as agent:
            result = await agent.process_command("Test the API connection")
            return result
    
    try:
        result = asyncio.run(_test())
        print("✅ Connection test completed:")
        print(result)
    except Exception as e:
        print(f"❌ Connection test failed: {e}")


def validate_config():
    """Validate the current configuration."""
    print_banner()
    print("Validating configuration...")
    print()
    
    try:
        config.validate()
        print("✅ Configuration is valid!")
        
        print("\n📋 Configuration Summary:")
        print(f"  Use MCP Servers: {config.use_mcp_servers}")
        print(f"  Use Custom API: {config.use_custom_api}")
        
        if config.use_mcp_servers:
            print(f"  Jira MCP Path: {config.mcp.jira_server_path or 'Default'}")
            print(f"  Confluence MCP Path: {config.mcp.confluence_server_path or 'Default'}")
        elif config.use_custom_api:
            print(f"  API Base URL: {config.api.base_url}")
            print(f"  API Version: {config.api.version}")
        else:
            print(f"  Jira URL: {config.jira.base_url or 'Not configured'}")
            print(f"  Confluence URL: {config.confluence.base_url or 'Not configured'}")
            
        print(f"  Log Level: {config.agent.log_level}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Tips:")
        print("  - Check your .env file exists")
        print("  - Verify all required variables are set")
        print("  - Run setup.sh for interactive configuration")


def show_examples():
    """Show example commands."""
    print_banner()
    print("📚 Example Commands:")
    print()
    
    examples = [
        # Jira examples
        ('Jira - Get Issue', '"Get issue DEMO-123"'),
        ('Jira - Search', '"Search for open bugs in project MYPROJ"'),
        ('Jira - Create', '"Create task in DEMO: Update documentation"'),
        ('Jira - Comment', '"Add comment to DEMO-123: Fixed in latest release"'),
        
        # Confluence examples
        ('Confluence - Get Page', '"Get page 12345"'),
        ('Confluence - Search', '"Search for pages about authentication"'),
        ('Confluence - Create', '"Create page in DEV space: API Integration Guide"'),
        
        # Java examples
        ('Java - Analyze', '"Analyze this Java code: public class Test { }"'),
        ('Java - Generate', '"Generate a UserService class with CRUD operations"'),
        
        # Combined examples
        ('Combined', '"Create documentation for issue DEMO-123 in DOCS space"'),
        
        # System examples
        ('System - Test', '"Test the API connection"'),
    ]
    
    for category, example in examples:
        print(f"  {category:<20} {example}")
    
    print()
    print("🚀 To run examples:")
    print("  python run.py execute 'Get issue DEMO-123'")
    print("  python run.py interactive")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Integration Agent Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py interactive              # Start interactive mode
  python run.py execute "Get issue DEMO-123"  # Execute single command
  python run.py test                     # Test API connection
  python run.py validate                 # Validate configuration
  python run.py examples                 # Show example commands
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Interactive mode
    subparsers.add_parser('interactive', help='Start interactive mode')
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute a single command')
    execute_parser.add_argument('query', help='Command to execute')
    execute_parser.add_argument('--context', help='JSON context for the command')
    
    # Test connection
    subparsers.add_parser('test', help='Test API connection')
    
    # Validate config
    subparsers.add_parser('validate', help='Validate configuration')
    
    # Show examples
    subparsers.add_parser('examples', help='Show example commands')
    
    args = parser.parse_args()
    
    if not args.command:
        print_banner()
        print("No command specified. Use --help for usage information.")
        print()
        print("Quick start:")
        print("  python run.py interactive    # Interactive mode")
        print("  python run.py examples       # Show examples")
        print("  python run.py validate       # Check configuration")
        return
    
    try:
        if args.command == 'interactive':
            asyncio.run(interactive_mode())
        elif args.command == 'execute':
            context = None
            if args.context:
                import json
                context = json.loads(args.context)
            asyncio.run(execute_command(args.query, context))
        elif args.command == 'test':
            test_connection()
        elif args.command == 'validate':
            validate_config()
        elif args.command == 'examples':
            show_examples()
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()