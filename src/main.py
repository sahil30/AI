#!/usr/bin/env python3
"""
AI Integration Agent - Main Entry Point
Supports Jira, Confluence, and Java code processing
"""

import asyncio
import sys
import json
import logging
from typing import Optional

import click

from .config import config
from .agent import AIAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@click.group()
@click.option('--debug', is_flag=True, help='Enable debug logging')
def cli(debug):
    """AI Integration Agent CLI"""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)

@cli.command()
def interactive():
    """Start interactive mode"""
    asyncio.run(run_interactive())

@cli.command()
@click.argument('command', type=str)
@click.option('--context', type=str, help='JSON context for the command')
def execute(command: str, context: Optional[str]):
    """Execute a single command"""
    context_dict = {}
    if context:
        try:
            context_dict = json.loads(context)
        except json.JSONDecodeError:
            click.echo("Error: Invalid JSON in context parameter", err=True)
            sys.exit(1)
    
    asyncio.run(run_single_command(command, context_dict))

@cli.command()
@click.argument('issue_key', type=str)
@click.argument('space_key', type=str)
def doc_from_issue(issue_key: str, space_key: str):
    """Generate Confluence documentation from a Jira issue"""
    asyncio.run(generate_documentation_from_issue(issue_key, space_key))

@cli.command()
@click.argument('project_path', type=click.Path(exists=True))
@click.option('--output', type=click.Path(), help='Output file for analysis results')
def analyze_java(project_path: str, output: Optional[str]):
    """Analyze a Java project"""
    asyncio.run(analyze_java_project(project_path, output))

@cli.command()
def validate_config():
    """Validate configuration"""
    try:
        config.validate()
        click.echo("✅ Configuration is valid!")
    except ValueError as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        sys.exit(1)

async def run_interactive():
    """Run the agent in interactive mode"""
    try:
        config.validate()
        agent = AIAgent()
        
        print("\n🤖 AI Integration Agent - Python Edition")
        print("Capabilities: Jira, Confluence, Java Code Processing")
        print("Type 'help' for available commands or 'exit' to quit\n")
        
        while True:
            try:
                command = input("AI Agent> ").strip()
                
                if command.lower() == 'exit':
                    print("Goodbye! 👋")
                    break
                
                if command.lower() == 'help':
                    show_help()
                    continue
                
                if not command:
                    continue
                
                print("🔄 Processing...")
                result = await agent.process_command(command)
                
                print("\n📋 Result:")
                print(json.dumps(result, indent=2, default=str))
                print()
                
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                logger.error(f"Command processing error: {str(e)}")
    
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your .env file and ensure all required variables are set.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start AI Agent: {str(e)}")
        sys.exit(1)

async def run_single_command(command: str, context: dict):
    """Execute a single command"""
    try:
        config.validate()
        agent = AIAgent()
        
        print("🔄 Processing command...")
        result = await agent.process_command(command, context)
        
        print("📋 Result:")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

async def generate_documentation_from_issue(issue_key: str, space_key: str):
    """Generate Confluence documentation from a Jira issue"""
    try:
        config.validate()
        agent = AIAgent()
        
        print(f"🔄 Generating documentation for {issue_key} in space {space_key}...")
        result = agent.analyze_jira_issue_and_generate_documentation(issue_key, space_key)
        
        print("✅ Documentation generated successfully!")
        print(f"📄 Page URL: {result['documentation'].get('_links', {}).get('webui', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

async def analyze_java_project(project_path: str, output: Optional[str]):
    """Analyze a Java project"""
    try:
        config.validate()
        agent = AIAgent()
        
        print(f"🔄 Analyzing Java project at {project_path}...")
        result = agent.analyze_java_project(project_path)
        
        if output:
            with open(output, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            print(f"✅ Analysis saved to {output}")
        else:
            print("📊 Analysis Results:")
            print(json.dumps(result['summary'], indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

def show_help():
    """Show help information"""
    help_text = """
📖 Available Commands:

JIRA Commands:
  - "Get issue PROJ-123" - Get a specific Jira issue
  - "Search issues in project PROJ" - Search issues using JQL
  - "Create issue in PROJ: Fix login bug" - Create a new issue
  - "Add comment to PROJ-123: Working on this" - Add comment

Confluence Commands:
  - "Get page 12345" - Get a Confluence page
  - "Search pages about authentication" - Search content
  - "Create page in SPACE: API Documentation" - Create new page

Java Code Commands:
  - "Analyze Java code: [paste code]" - Analyze code structure
  - "Generate class UserService" - Generate Java class
  - "Create documentation for issue PROJ-123 in SPACE" - Auto-generate docs

General Commands:
  - "help" - Show this help
  - "exit" - Exit the application

💡 Examples:
  - "Get issue ABC-123"
  - "Search issues: project = MYPROJ AND status = Open"
  - "Analyze Java project /path/to/project"
  - "Create documentation for ABC-123 in DEV"

🔧 CLI Commands:
  - ai-agent interactive - Start interactive mode
  - ai-agent execute "command" - Execute single command
  - ai-agent doc-from-issue ABC-123 SPACE - Generate docs
  - ai-agent analyze-java /path/to/project - Analyze Java code
  - ai-agent validate-config - Check configuration
"""
    print(help_text)

def main():
    """Main entry point"""
    cli()

if __name__ == '__main__':
    main()