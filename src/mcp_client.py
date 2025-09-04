"""MCP client for communicating with Jira and Confluence MCP servers."""

import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import os

logger = logging.getLogger(__name__)


@dataclass
class MCPResponse:
    """Response from MCP server."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


class MCPServerClient:
    """Client for communicating with MCP servers."""
    
    def __init__(self, server_path: str, server_module: str):
        self.server_path = server_path
        self.server_module = server_module
        self.process = None
        self.timeout = 30
    
    async def start_server(self) -> bool:
        """Start the MCP server process."""
        try:
            # Change to server directory and start the server
            cmd = ["python", "-m", self.server_module]
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=self.server_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give the server a moment to start
            await asyncio.sleep(1)
            
            if self.process.returncode is None:
                logger.info(f"MCP server started successfully: {self.server_module}")
                return True
            else:
                logger.error(f"Failed to start MCP server: {self.server_module}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting MCP server {self.server_module}: {str(e)}")
            return False
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process and self.process.returncode is None:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5)
            except asyncio.TimeoutError:
                self.process.kill()
                await self.process.wait()
            logger.info(f"MCP server stopped: {self.server_module}")
    
    async def send_request(self, method: str, params: Dict[str, Any]) -> MCPResponse:
        """Send a request to the MCP server."""
        if not self.process or self.process.returncode is not None:
            return MCPResponse(success=False, error="Server not running")
        
        try:
            # Create MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": method,
                "params": params
            }
            
            # Send request
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json.encode())
            await self.process.stdin.drain()
            
            # Read response
            response_data = await asyncio.wait_for(
                self.process.stdout.readline(),
                timeout=self.timeout
            )
            
            if not response_data:
                return MCPResponse(success=False, error="No response from server")
            
            response = json.loads(response_data.decode().strip())
            
            if "error" in response:
                return MCPResponse(success=False, error=response["error"].get("message", "Unknown error"))
            
            return MCPResponse(success=True, data=response.get("result"))
            
        except asyncio.TimeoutError:
            return MCPResponse(success=False, error="Request timeout")
        except Exception as e:
            return MCPResponse(success=False, error=f"Request failed: {str(e)}")


class MCPJiraClient:
    """Client for Jira MCP server."""
    
    def __init__(self, server_path: str):
        self.client = MCPServerClient(server_path, "mcp_jira_server.server")
    
    async def start(self) -> bool:
        """Start the Jira MCP server."""
        return await self.client.start_server()
    
    async def stop(self):
        """Stop the Jira MCP server."""
        await self.client.stop_server()
    
    async def get_issue(self, issue_key: str) -> MCPResponse:
        """Get a specific issue by key."""
        return await self.client.send_request("tools/call", {
            "name": "jira_get_issue",
            "arguments": {"issue_key": issue_key}
        })
    
    async def search_issues(self, jql: str, max_results: int = 50) -> MCPResponse:
        """Search for issues using JQL."""
        return await self.client.send_request("tools/call", {
            "name": "jira_search_issues",
            "arguments": {"jql": jql, "max_results": max_results}
        })
    
    async def create_issue(self, project_key: str, summary: str, **kwargs) -> MCPResponse:
        """Create a new issue."""
        params = {
            "project_key": project_key,
            "summary": summary,
            **kwargs
        }
        return await self.client.send_request("tools/call", {
            "name": "jira_create_issue",
            "arguments": params
        })
    
    async def add_comment(self, issue_key: str, comment: str) -> MCPResponse:
        """Add a comment to an issue."""
        return await self.client.send_request("tools/call", {
            "name": "jira_add_comment",
            "arguments": {"issue_key": issue_key, "comment": comment}
        })
    
    async def get_projects(self) -> MCPResponse:
        """Get all projects."""
        return await self.client.send_request("tools/call", {
            "name": "jira_get_projects",
            "arguments": {}
        })


class MCPConfluenceClient:
    """Client for Confluence MCP server."""
    
    def __init__(self, server_path: str):
        self.client = MCPServerClient(server_path, "mcp_confluence_server.server")
    
    async def start(self) -> bool:
        """Start the Confluence MCP server."""
        return await self.client.start_server()
    
    async def stop(self):
        """Stop the Confluence MCP server."""
        await self.client.stop_server()
    
    async def get_page(self, page_id: str) -> MCPResponse:
        """Get a specific page by ID."""
        return await self.client.send_request("tools/call", {
            "name": "confluence_get_page",
            "arguments": {"page_id": page_id}
        })
    
    async def search_content(self, query: str, space_key: Optional[str] = None) -> MCPResponse:
        """Search for content."""
        params = {"query": query}
        if space_key:
            params["space_key"] = space_key
        
        return await self.client.send_request("tools/call", {
            "name": "confluence_search_content",
            "arguments": params
        })
    
    async def create_page(self, space_key: str, title: str, content: str, **kwargs) -> MCPResponse:
        """Create a new page."""
        params = {
            "space_key": space_key,
            "title": title,
            "content": content,
            **kwargs
        }
        return await self.client.send_request("tools/call", {
            "name": "confluence_create_page",
            "arguments": params
        })
    
    async def get_spaces(self) -> MCPResponse:
        """Get all spaces."""
        return await self.client.send_request("tools/call", {
            "name": "confluence_get_spaces",
            "arguments": {}
        })
    
    async def add_comment(self, page_id: str, comment: str) -> MCPResponse:
        """Add a comment to a page."""
        return await self.client.send_request("tools/call", {
            "name": "confluence_add_comment",
            "arguments": {"page_id": page_id, "comment": comment}
        })


class MCPManager:
    """Manager for multiple MCP clients."""
    
    def __init__(self, jira_server_path: Optional[str] = None, confluence_server_path: Optional[str] = None):
        self.jira_client = MCPJiraClient(jira_server_path) if jira_server_path else None
        self.confluence_client = MCPConfluenceClient(confluence_server_path) if confluence_server_path else None
        self.started = False
    
    async def start(self) -> bool:
        """Start all MCP servers."""
        success = True
        
        if self.jira_client:
            jira_started = await self.jira_client.start()
            if not jira_started:
                logger.error("Failed to start Jira MCP server")
                success = False
        
        if self.confluence_client:
            confluence_started = await self.confluence_client.start()
            if not confluence_started:
                logger.error("Failed to start Confluence MCP server")
                success = False
        
        self.started = success
        return success
    
    async def stop(self):
        """Stop all MCP servers."""
        if self.jira_client:
            await self.jira_client.stop()
        
        if self.confluence_client:
            await self.confluence_client.stop()
        
        self.started = False
    
    def is_ready(self) -> bool:
        """Check if MCP servers are ready."""
        return self.started
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()