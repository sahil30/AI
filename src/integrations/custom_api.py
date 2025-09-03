import requests
import json
from typing import Dict, List, Optional, Any, Union
from ..config import config
import logging

logger = logging.getLogger(__name__)

class CustomAPIIntegration:
    """Generic integration for custom APIs with flexible endpoint mapping."""
    
    def __init__(self):
        if not config.use_custom_api:
            raise ValueError("Custom API integration requires USE_CUSTOM_API=true")
            
        self.base_url = config.api.base_url.rstrip('/')
        self.api_key = config.api.api_key
        self.version = config.api.version
        self.timeout = config.agent.timeout_seconds
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'AI-Integration-Agent/1.0'
        })
        
        # Define default endpoint mappings - can be customized
        self.endpoints = {
            # Issue/Ticket endpoints
            'issues': {
                'list': f'/{self.version}/issues',
                'get': f'/{self.version}/issues/{{id}}',
                'create': f'/{self.version}/issues',
                'update': f'/{self.version}/issues/{{id}}',
                'search': f'/{self.version}/issues/search',
                'comments': f'/{self.version}/issues/{{id}}/comments',
                'transitions': f'/{self.version}/issues/{{id}}/transitions'
            },
            # Documentation/Page endpoints
            'pages': {
                'list': f'/{self.version}/pages',
                'get': f'/{self.version}/pages/{{id}}',
                'create': f'/{self.version}/pages',
                'update': f'/{self.version}/pages/{{id}}',
                'search': f'/{self.version}/pages/search',
                'spaces': f'/{self.version}/spaces'
            },
            # Project/Space endpoints
            'projects': {
                'list': f'/{self.version}/projects',
                'get': f'/{self.version}/projects/{{id}}',
                'create': f'/{self.version}/projects',
                'update': f'/{self.version}/projects/{{id}}'
            }
        }

    def configure_endpoints(self, endpoint_config: Dict[str, Dict[str, str]]):
        """Allow customization of API endpoints."""
        self.endpoints.update(endpoint_config)

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make an HTTP request to the API."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            
            # Handle empty responses
            if not response.text:
                return {}
                
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise Exception(f"API request failed: {str(e)}")

    # Issue/Ticket Management
    def get_issue(self, issue_id: str) -> Dict[str, Any]:
        """Get a specific issue/ticket by ID."""
        endpoint = self.endpoints['issues']['get'].format(id=issue_id)
        return self._make_request('GET', endpoint)

    def search_issues(self, query: str = "", filters: Dict[str, Any] = None, limit: int = 50) -> Dict[str, Any]:
        """Search for issues/tickets."""
        endpoint = self.endpoints['issues']['search']
        params = {'limit': limit}
        
        if query:
            params['q'] = query
        
        if filters:
            params.update(filters)
            
        return self._make_request('GET', endpoint, params=params)

    def create_issue(self, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new issue/ticket."""
        endpoint = self.endpoints['issues']['create']
        return self._make_request('POST', endpoint, json=issue_data)

    def update_issue(self, issue_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing issue/ticket."""
        endpoint = self.endpoints['issues']['update'].format(id=issue_id)
        return self._make_request('PUT', endpoint, json=update_data)

    def add_comment(self, issue_id: str, comment: str, **kwargs) -> Dict[str, Any]:
        """Add a comment to an issue/ticket."""
        endpoint = self.endpoints['issues']['comments'].format(id=issue_id)
        comment_data = {
            'comment': comment,
            'author': kwargs.get('author', 'AI Agent'),
            **kwargs
        }
        return self._make_request('POST', endpoint, json=comment_data)

    def get_comments(self, issue_id: str) -> List[Dict[str, Any]]:
        """Get comments for an issue/ticket."""
        endpoint = self.endpoints['issues']['comments'].format(id=issue_id)
        response = self._make_request('GET', endpoint)
        return response.get('comments', response.get('data', []))

    def transition_issue(self, issue_id: str, transition: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Transition an issue to a new status."""
        endpoint = self.endpoints['issues']['transitions'].format(id=issue_id)
        
        if isinstance(transition, str):
            transition_data = {'status': transition}
        else:
            transition_data = transition
            
        return self._make_request('POST', endpoint, json=transition_data)

    def get_transitions(self, issue_id: str) -> List[Dict[str, Any]]:
        """Get available transitions for an issue."""
        endpoint = self.endpoints['issues']['transitions'].format(id=issue_id)
        response = self._make_request('GET', endpoint)
        return response.get('transitions', response.get('data', []))

    # Project Management
    def get_projects(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all projects."""
        endpoint = self.endpoints['projects']['list']
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.get('projects', response.get('data', []))

    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get a specific project."""
        endpoint = self.endpoints['projects']['get'].format(id=project_id)
        return self._make_request('GET', endpoint)

    # Page/Document Management
    def get_page(self, page_id: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get a specific page/document."""
        endpoint = self.endpoints['pages']['get'].format(id=page_id)
        params = {}
        
        if expand:
            params['expand'] = ','.join(expand)
            
        return self._make_request('GET', endpoint, params=params)

    def search_pages(self, query: str = "", space_id: str = None, limit: int = 25) -> Dict[str, Any]:
        """Search for pages/documents."""
        endpoint = self.endpoints['pages']['search']
        params = {'limit': limit}
        
        if query:
            params['q'] = query
        if space_id:
            params['space'] = space_id
            
        return self._make_request('GET', endpoint, params=params)

    def create_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new page/document."""
        endpoint = self.endpoints['pages']['create']
        return self._make_request('POST', endpoint, json=page_data)

    def update_page(self, page_id: str, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing page/document."""
        endpoint = self.endpoints['pages']['update'].format(id=page_id)
        return self._make_request('PUT', endpoint, json=page_data)

    def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Delete a page/document."""
        endpoint = self.endpoints['pages']['get'].format(id=page_id)
        return self._make_request('DELETE', endpoint)

    def get_spaces(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all spaces/containers."""
        endpoint = self.endpoints['pages']['spaces']
        params = {'limit': limit}
        response = self._make_request('GET', endpoint, params=params)
        return response.get('spaces', response.get('data', []))

    # Generic API methods for custom endpoints
    def get(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a generic GET request."""
        return self._make_request('GET', endpoint, params=params)

    def post(self, endpoint: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a generic POST request."""
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        return self._make_request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, data: Dict[str, Any] = None, json_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a generic PUT request."""
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        return self._make_request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a generic DELETE request."""
        return self._make_request('DELETE', endpoint, params=params)

    # Utility methods
    def test_connection(self) -> Dict[str, Any]:
        """Test the API connection."""
        try:
            # Try a simple endpoint that should exist
            response = self.get('/health')
            return {'status': 'connected', 'response': response}
        except Exception as e:
            try:
                # Fallback to root endpoint
                response = self.get('/')
                return {'status': 'connected', 'response': response}
            except Exception as e2:
                return {'status': 'failed', 'error': str(e2)}

    def get_api_info(self) -> Dict[str, Any]:
        """Get API information and capabilities."""
        return {
            'base_url': self.base_url,
            'version': self.version,
            'endpoints': self.endpoints,
            'configured': True
        }