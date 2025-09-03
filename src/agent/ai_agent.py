import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI

from ..config import config
from ..integrations import (
    JiraIntegration, ConfluenceIntegration, JavaProcessor,
    AdaptiveJiraIntegration, AdaptiveConfluenceIntegration, CustomAPIIntegration
)

logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.openai_client = OpenAI(api_key=config.openai.api_key)
        
        # Use adaptive integrations that can work with both standard and custom APIs
        self.jira = AdaptiveJiraIntegration()
        self.confluence = AdaptiveConfluenceIntegration()
        self.java_processor = JavaProcessor()
        
        # Also store direct access to custom API if available
        if config.use_custom_api:
            self.custom_api = CustomAPIIntegration()
        else:
            self.custom_api = None
        
        # Set up logging
        logging.basicConfig(
            level=getattr(logging, config.agent.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def process_command(self, command: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a natural language command and execute appropriate actions."""
        if context is None:
            context = {}
            
        try:
            logger.info(f"Processing command: {command}")
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": f"Command: {command}\nContext: {json.dumps(context)}"
                    }
                ],
                functions=self._get_function_definitions(),
                function_call="auto"
            )
            
            message = response.choices[0].message
            
            if message.function_call:
                return await self._execute_function(message.function_call)
            
            return {
                'type': 'response',
                'content': message.content
            }
            
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            raise e

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the AI agent."""
        api_type = "custom API" if config.use_custom_api else "standard Atlassian APIs"
        
        return f"""You are an AI agent that can interact with issue tracking, documentation, and Java code systems.
        You are currently configured to use {api_type} for backend operations.
        
        You have access to the following capabilities:
        
        ISSUE/TICKET OPERATIONS (via {api_type}):
        - Get, search, create, update issues/tickets
        - Add comments and manage status transitions
        - Access project information
        
        DOCUMENTATION/WIKI OPERATIONS (via {api_type}):
        - Read, create, update, delete pages/documents
        - Search content and manage spaces/collections
        - Add comments and handle content formats
        
        JAVA CODE OPERATIONS:
        - Analyze Java code structure and complexity
        - Generate Java classes and methods
        - Parse and extract code information
        - Write Java files
        
        When users request actions, determine the appropriate integration to use and call the relevant functions.
        The system will automatically handle API format differences between standard and custom APIs.
        Provide clear, helpful responses and ask for clarification when needed.
        
        Always consider the context provided and use it to make better decisions about which actions to take."""

    def _get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get function definitions for OpenAI function calling."""
        return [
            # Jira functions
            {
                "name": "jira_get_issue",
                "description": "Get a specific Jira issue by key",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string", "description": "The Jira issue key (e.g., PROJ-123)"}
                    },
                    "required": ["issue_key"]
                }
            },
            {
                "name": "jira_search_issues",
                "description": "Search for Jira issues using JQL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "jql": {"type": "string", "description": "JQL query string"},
                        "fields": {"type": "array", "items": {"type": "string"}, "description": "Fields to return"}
                    },
                    "required": ["jql"]
                }
            },
            {
                "name": "jira_create_issue",
                "description": "Create a new Jira issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "project_key": {"type": "string", "description": "Project key"},
                        "issue_data": {
                            "type": "object",
                            "properties": {
                                "summary": {"type": "string"},
                                "description": {"type": "string"},
                                "issue_type": {"type": "string"}
                            },
                            "required": ["summary"]
                        }
                    },
                    "required": ["project_key", "issue_data"]
                }
            },
            {
                "name": "jira_add_comment",
                "description": "Add a comment to a Jira issue",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "issue_key": {"type": "string"},
                        "comment": {"type": "string"}
                    },
                    "required": ["issue_key", "comment"]
                }
            },
            # Confluence functions
            {
                "name": "confluence_get_page",
                "description": "Get a Confluence page by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "page_id": {"type": "string", "description": "Page ID"}
                    },
                    "required": ["page_id"]
                }
            },
            {
                "name": "confluence_search_content",
                "description": "Search Confluence content using CQL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "cql": {"type": "string", "description": "Confluence Query Language string"},
                        "limit": {"type": "integer", "description": "Maximum number of results"}
                    },
                    "required": ["cql"]
                }
            },
            {
                "name": "confluence_create_page",
                "description": "Create a new Confluence page",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "space_key": {"type": "string"},
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "parent_page_id": {"type": "string"}
                    },
                    "required": ["space_key", "title", "content"]
                }
            },
            # Java functions
            {
                "name": "java_analyze_code",
                "description": "Analyze Java code structure and complexity",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Java code to analyze"},
                        "file_name": {"type": "string", "description": "Optional file name"}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "java_generate_class",
                "description": "Generate a Java class",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "class_name": {"type": "string"},
                        "options": {
                            "type": "object",
                            "properties": {
                                "package_name": {"type": "string"},
                                "imports": {"type": "array", "items": {"type": "string"}},
                                "super_class": {"type": "string"},
                                "interfaces": {"type": "array", "items": {"type": "string"}},
                                "methods": {"type": "array"},
                                "fields": {"type": "array"}
                            }
                        }
                    },
                    "required": ["class_name"]
                }
            },
            {
                "name": "java_write_file",
                "description": "Write Java code to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["file_path", "content"]
                }
            },
            # Custom API functions (available when using custom API)
            {
                "name": "custom_api_get",
                "description": "Make a GET request to a custom API endpoint",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string", "description": "API endpoint path"},
                        "params": {"type": "object", "description": "Query parameters"}
                    },
                    "required": ["endpoint"]
                }
            },
            {
                "name": "custom_api_post",
                "description": "Make a POST request to a custom API endpoint",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "endpoint": {"type": "string", "description": "API endpoint path"},
                        "data": {"type": "object", "description": "Request body data"}
                    },
                    "required": ["endpoint", "data"]
                }
            },
            {
                "name": "test_api_connection",
                "description": "Test the API connection and get system information",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        ]

    async def _execute_function(self, function_call) -> Dict[str, Any]:
        """Execute a function call from OpenAI."""
        function_name = function_call.name
        function_args = json.loads(function_call.arguments)
        
        logger.info(f"Executing function: {function_name} with args: {function_args}")
        
        try:
            # Jira functions
            if function_name == "jira_get_issue":
                issue = self.jira.get_issue(function_args["issue_key"])
                return {"type": "jira_issue", "data": issue}
                
            elif function_name == "jira_search_issues":
                results = self.jira.search_issues(function_args["jql"], function_args.get("fields"))
                return {"type": "jira_search", "data": results}
                
            elif function_name == "jira_create_issue":
                new_issue = self.jira.create_issue(function_args["project_key"], function_args["issue_data"])
                return {"type": "jira_issue_created", "data": new_issue}
                
            elif function_name == "jira_add_comment":
                comment = self.jira.add_comment(function_args["issue_key"], function_args["comment"])
                return {"type": "jira_comment_added", "data": comment}
            
            # Confluence functions
            elif function_name == "confluence_get_page":
                page = self.confluence.get_page(function_args["page_id"])
                return {"type": "confluence_page", "data": page}
                
            elif function_name == "confluence_search_content":
                content = self.confluence.search_content(
                    function_args["cql"], 
                    limit=function_args.get("limit", 25)
                )
                return {"type": "confluence_search", "data": content}
                
            elif function_name == "confluence_create_page":
                new_page = self.confluence.create_page(
                    function_args["space_key"],
                    function_args["title"],
                    function_args["content"],
                    function_args.get("parent_page_id")
                )
                return {"type": "confluence_page_created", "data": new_page}
            
            # Java functions
            elif function_name == "java_analyze_code":
                analysis = self.java_processor.analyze_java_code(
                    function_args["code"],
                    function_args.get("file_name", "unknown")
                )
                return {"type": "java_analysis", "data": analysis}
                
            elif function_name == "java_generate_class":
                generated_code = self.java_processor.generate_java_class(
                    function_args["class_name"],
                    function_args.get("options", {})
                )
                return {"type": "java_code_generated", "data": {"code": generated_code}}
                
            elif function_name == "java_write_file":
                self.java_processor.write_java_file(function_args["file_path"], function_args["content"])
                return {"type": "java_file_written", "data": {"file_path": function_args["file_path"]}}
            
            # Custom API functions
            elif function_name == "custom_api_get":
                if not self.custom_api:
                    return {"type": "error", "message": "Custom API not configured"}
                result = self.custom_api.get(function_args["endpoint"], function_args.get("params"))
                return {"type": "custom_api_response", "data": result}
                
            elif function_name == "custom_api_post":
                if not self.custom_api:
                    return {"type": "error", "message": "Custom API not configured"}
                result = self.custom_api.post(function_args["endpoint"], json_data=function_args["data"])
                return {"type": "custom_api_response", "data": result}
                
            elif function_name == "test_api_connection":
                if self.custom_api:
                    connection_info = self.custom_api.test_connection()
                    api_info = self.custom_api.get_api_info()
                    return {"type": "api_test", "data": {"connection": connection_info, "info": api_info}}
                else:
                    # Test standard APIs
                    results = {}
                    try:
                        # Test if we can access projects/spaces
                        projects = self.jira.get_projects() if hasattr(self.jira, 'get_projects') else []
                        results['jira'] = {"status": "connected", "projects_count": len(projects)}
                    except Exception as e:
                        results['jira'] = {"status": "failed", "error": str(e)}
                    
                    try:
                        spaces = self.confluence.get_spaces() if hasattr(self.confluence, 'get_spaces') else {"results": []}
                        results['confluence'] = {"status": "connected", "spaces_count": len(spaces.get('results', []))}
                    except Exception as e:
                        results['confluence'] = {"status": "failed", "error": str(e)}
                    
                    return {"type": "api_test", "data": results}
            
            else:
                raise Exception(f"Unknown function: {function_name}")
                
        except Exception as e:
            logger.error(f"Function execution error: {str(e)}")
            return {"type": "error", "message": str(e)}

    def analyze_jira_issue_and_generate_documentation(self, issue_key: str, space_key: str) -> Dict[str, Any]:
        """Analyze a Jira issue and generate Confluence documentation."""
        try:
            issue = self.jira.get_issue(issue_key)
            comments = self.jira.get_comments(issue_key)
            
            documentation_content = self._generate_issue_documentation(issue, comments)
            
            page = self.confluence.create_page(
                space_key,
                f"Documentation for {issue_key}: {issue['fields']['summary']}",
                documentation_content
            )
            
            return {
                'issue': issue,
                'documentation': page,
                'message': f"Created documentation page for {issue_key}"
            }
        except Exception as e:
            logger.error(f"Error analyzing issue and generating documentation: {str(e)}")
            raise e

    def _generate_issue_documentation(self, issue: Dict[str, Any], comments: List[Dict[str, Any]]) -> str:
        """Generate HTML documentation content for a Jira issue."""
        content = f"<h1>{issue['fields']['summary']}</h1>"
        content += f"<p><strong>Issue Key:</strong> {issue['key']}</p>"
        content += f"<p><strong>Status:</strong> {issue['fields']['status']['name']}</p>"
        content += f"<p><strong>Type:</strong> {issue['fields']['issuetype']['name']}</p>"
        
        if issue['fields'].get('assignee'):
            content += f"<p><strong>Assignee:</strong> {issue['fields']['assignee']['displayName']}</p>"
        
        content += "<h2>Description</h2>"
        description = issue['fields'].get('description', 'No description provided')
        if isinstance(description, dict):
            # Handle ADF (Atlassian Document Format)
            description = self._extract_text_from_adf(description)
        content += f"<p>{description}</p>"
        
        if comments:
            content += "<h2>Comments</h2>"
            for comment in comments:
                author = comment['author']['displayName']
                body = comment['body']
                if isinstance(body, dict):
                    body = self._extract_text_from_adf(body)
                content += f"<div><strong>{author}:</strong> {body}</div>"
        
        return content

    def _extract_text_from_adf(self, adf_content: Dict[str, Any]) -> str:
        """Extract plain text from Atlassian Document Format."""
        if not adf_content or not isinstance(adf_content, dict):
            return ""
        
        text_parts = []
        
        def extract_text(node):
            if isinstance(node, dict):
                if node.get('type') == 'text':
                    text_parts.append(node.get('text', ''))
                elif 'content' in node:
                    for child in node['content']:
                        extract_text(child)
            elif isinstance(node, list):
                for item in node:
                    extract_text(item)
        
        extract_text(adf_content)
        return ' '.join(text_parts)

    def analyze_java_project(self, project_path: str) -> Dict[str, Any]:
        """Analyze a Java project and return comprehensive metrics."""
        try:
            java_files = self.java_processor.find_java_files(project_path)
            analyses = []
            
            for file_path in java_files:
                analysis = self.java_processor.analyze_java_file(file_path)
                analyses.append(analysis)
            
            summary = self._generate_project_summary(analyses)
            
            return {
                'files': analyses,
                'summary': summary,
                'metrics': self._calculate_project_metrics(analyses)
            }
        except Exception as e:
            logger.error(f"Error analyzing Java project: {str(e)}")
            raise e

    def _generate_project_summary(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of the Java project analysis."""
        total_files = len(analyses)
        total_lines = sum(analysis['lines_of_code'] for analysis in analyses)
        total_classes = sum(len(analysis['classes']) for analysis in analyses)
        total_methods = sum(len(analysis['methods']) for analysis in analyses)
        avg_complexity = sum(analysis['complexity'] for analysis in analyses) / total_files if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'total_lines': total_lines,
            'total_classes': total_classes,
            'total_methods': total_methods,
            'avg_complexity': round(avg_complexity, 2)
        }

    def _calculate_project_metrics(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate detailed project metrics."""
        complexity_distribution = [
            {'file': analysis['file_name'], 'complexity': analysis['complexity']} 
            for analysis in analyses
        ]
        
        largest_files = sorted(
            analyses, 
            key=lambda x: x['lines_of_code'], 
            reverse=True
        )[:10]
        
        # Flatten all methods and sort by complexity
        all_methods = []
        for analysis in analyses:
            for method in analysis['methods']:
                method_with_file = method.copy()
                method_with_file['file'] = analysis['file_name']
                all_methods.append(method_with_file)
        
        most_complex_methods = sorted(
            all_methods,
            key=lambda x: x.get('complexity', 0),
            reverse=True
        )[:10]
        
        return {
            'complexity_distribution': complexity_distribution,
            'largest_files': largest_files,
            'most_complex_methods': most_complex_methods
        }