#!/usr/bin/env python3
"""
Example usage of the AI Integration Agent
"""

import asyncio
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import config
from agent import AIAgent

async def run_examples():
    """Run example commands to demonstrate the AI agent capabilities."""
    try:
        config.validate()
        agent = AIAgent()
        
        print("🤖 AI Agent Examples - Python Edition\n")

        # Example 1: Get a Jira issue
        print("📋 Example 1: Getting Jira Issue")
        try:
            result1 = await agent.process_command('Get issue DEMO-1')
            print("Result:", json.dumps(result1, indent=2, default=str))
        except Exception as e:
            print(f"Note: Replace DEMO-1 with a real issue key from your Jira instance. Error: {e}")
        print("\n---\n")

        # Example 2: Search Jira issues
        print("📋 Example 2: Searching Jira Issues")
        try:
            result2 = await agent.process_command('Search issues: project = DEMO AND status = "To Do"')
            print("Result:", json.dumps(result2, indent=2, default=str))
        except Exception as e:
            print(f"Note: Adjust the JQL query for your project. Error: {e}")
        print("\n---\n")

        # Example 3: Analyze Java code
        print("☕ Example 3: Analyzing Java Code")
        java_code = """
package com.example.service;

import java.util.List;
import java.util.Optional;

/**
 * User service for managing user operations
 */
public class UserService {
    
    private UserRepository userRepository;
    
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    public Optional<User> findById(Long id) {
        if (id == null || id <= 0) {
            return Optional.empty();
        }
        return userRepository.findById(id);
    }
    
    public List<User> findAll() {
        return userRepository.findAll();
    }
    
    public User save(User user) {
        if (user == null) {
            throw new IllegalArgumentException("User cannot be null");
        }
        return userRepository.save(user);
    }
}"""

        result3 = await agent.process_command(f"Analyze this Java code: {java_code}")
        print("Java Analysis Result:", json.dumps(result3, indent=2, default=str))
        print("\n---\n")

        # Example 4: Generate Java class
        print("☕ Example 4: Generating Java Class")
        result4 = await agent.process_command('Generate a ProductService class with CRUD operations')
        print("Generated Class Result:", json.dumps(result4, indent=2, default=str))
        print("\n---\n")

        # Example 5: Search Confluence content
        print("📖 Example 5: Searching Confluence Content")
        try:
            result5 = await agent.process_command('Search Confluence for "API documentation"')
            print("Confluence Search Result:", json.dumps(result5, indent=2, default=str))
        except Exception as e:
            print(f"Note: Adjust the search query for your Confluence instance. Error: {e}")

        # Example 6: Direct method calls (not through natural language)
        print("\n---\n")
        print("🔧 Example 6: Direct Java Analysis")
        try:
            analysis = agent.java_processor.analyze_java_code(java_code, "UserService.java")
            print("Direct Analysis:")
            print(f"  Classes: {len(analysis['classes'])}")
            print(f"  Methods: {len(analysis['methods'])}")
            print(f"  Complexity: {analysis['complexity']}")
            print(f"  Lines of code: {analysis['lines_of_code']}")
        except Exception as e:
            print(f"Error in direct analysis: {e}")

    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\n💡 Make sure to:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Jira, Confluence, and OpenAI credentials")
        print("3. Ensure your Jira/Confluence instances are accessible")
    except Exception as e:
        print(f"Example execution error: {e}")

def test_java_generation():
    """Test Java code generation without API calls."""
    print("\n🧪 Testing Java Code Generation (Offline)")
    
    try:
        from integrations import JavaProcessor
        java_processor = JavaProcessor()
        
        # Generate a sample class
        options = {
            'package_name': 'com.example.service',
            'imports': ['java.util.List', 'org.springframework.stereotype.Service'],
            'annotations': ['Service'],
            'fields': [
                {'name': 'repository', 'type': 'UserRepository', 'modifiers': ['private', 'final']},
            ],
            'methods': [
                {
                    'name': 'findAll',
                    'return_type': 'List<User>',
                    'modifiers': ['public'],
                    'body': '        return repository.findAll();'
                },
                {
                    'name': 'findById',
                    'return_type': 'Optional<User>',
                    'parameters': [{'name': 'id', 'type': 'Long'}],
                    'modifiers': ['public'],
                    'body': '        return repository.findById(id);'
                }
            ]
        }
        
        generated_class = java_processor.generate_java_class('UserService', options)
        print("Generated Java Class:")
        print(generated_class)
        
    except Exception as e:
        print(f"Error in Java generation test: {e}")

if __name__ == "__main__":
    # Run async examples
    asyncio.run(run_examples())
    
    # Run synchronous Java generation test
    test_java_generation()