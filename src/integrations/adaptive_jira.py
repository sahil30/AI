from typing import Dict, List, Optional, Any
from ..config import config
from .jira_integration import JiraIntegration
from .custom_api import CustomAPIIntegration
import logging

logger = logging.getLogger(__name__)

class AdaptiveJiraIntegration:
    """
    Adaptive Jira integration that can work with either standard Atlassian Jira API
    or your custom API that provides Jira-like functionality.
    """
    
    def __init__(self):
        if config.use_custom_api:
            self.backend = CustomAPIIntegration()
            self.is_custom = True
            logger.info("Using custom API for Jira operations")
        else:
            self.backend = JiraIntegration()
            self.is_custom = False
            logger.info("Using standard Atlassian Jira API")

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get a specific Jira issue by key."""
        if self.is_custom:
            # Custom API might use different field names
            response = self.backend.get_issue(issue_key)
            return self._normalize_issue_response(response)
        else:
            return self.backend.get_issue(issue_key)

    def search_issues(self, query: str, fields: List[str] = None) -> Dict[str, Any]:
        """Search for Jira issues."""
        if self.is_custom:
            # Convert JQL-like query to custom API format
            filters = self._parse_jql_to_filters(query)
            response = self.backend.search_issues(query, filters)
            return self._normalize_search_response(response)
        else:
            return self.backend.search_issues(query, fields)

    def create_issue(self, project_key: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira issue."""
        if self.is_custom:
            # Transform issue data to custom API format
            custom_data = self._transform_issue_data_to_custom(project_key, issue_data)
            response = self.backend.create_issue(custom_data)
            return self._normalize_issue_response(response)
        else:
            return self.backend.create_issue(project_key, issue_data)

    def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira issue."""
        if self.is_custom:
            custom_data = self._transform_update_data_to_custom(update_data)
            response = self.backend.update_issue(issue_key, custom_data)
            return self._normalize_issue_response(response)
        else:
            return self.backend.update_issue(issue_key, update_data)

    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a Jira issue."""
        if self.is_custom:
            response = self.backend.add_comment(issue_key, comment)
            return self._normalize_comment_response(response)
        else:
            return self.backend.add_comment(issue_key, comment)

    def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get comments for a Jira issue."""
        if self.is_custom:
            comments = self.backend.get_comments(issue_key)
            return [self._normalize_comment_response(comment) for comment in comments]
        else:
            return self.backend.get_comments(issue_key)

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        if self.is_custom:
            projects = self.backend.get_projects()
            return [self._normalize_project_response(project) for project in projects]
        else:
            return self.backend.get_projects()

    def transition_issue(self, issue_key: str, transition_id: str) -> Dict[str, Any]:
        """Transition a Jira issue."""
        if self.is_custom:
            response = self.backend.transition_issue(issue_key, transition_id)
            return response
        else:
            return self.backend.transition_issue(issue_key, transition_id)

    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for a Jira issue."""
        if self.is_custom:
            transitions = self.backend.get_transitions(issue_key)
            return [self._normalize_transition_response(t) for t in transitions]
        else:
            return self.backend.get_transitions(issue_key)

    # Normalization methods for custom API responses
    def _normalize_issue_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API issue response to Jira-like format."""
        if not self.is_custom:
            return response
            
        # Map common custom API fields to Jira fields
        normalized = {
            'key': response.get('id') or response.get('key') or response.get('number'),
            'id': response.get('id') or response.get('issue_id'),
            'fields': {}
        }
        
        # Map fields
        field_mapping = {
            'summary': ['title', 'summary', 'subject', 'name'],
            'description': ['description', 'body', 'content', 'details'],
            'status': ['status', 'state', 'stage'],
            'assignee': ['assignee', 'assigned_to', 'owner'],
            'reporter': ['reporter', 'created_by', 'author'],
            'created': ['created', 'created_at', 'date_created'],
            'updated': ['updated', 'updated_at', 'date_updated', 'modified'],
            'priority': ['priority', 'priority_level'],
            'labels': ['labels', 'tags'],
            'project': ['project', 'project_key', 'space']
        }
        
        for jira_field, possible_fields in field_mapping.items():
            for field in possible_fields:
                if field in response:
                    normalized['fields'][jira_field] = response[field]
                    break
        
        # Handle nested status object
        if isinstance(normalized['fields'].get('status'), str):
            normalized['fields']['status'] = {
                'name': normalized['fields']['status'],
                'id': normalized['fields']['status']
            }
        
        # Handle nested assignee object
        if isinstance(normalized['fields'].get('assignee'), str):
            normalized['fields']['assignee'] = {
                'displayName': normalized['fields']['assignee'],
                'name': normalized['fields']['assignee']
            }
            
        return normalized

    def _normalize_search_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API search response to Jira-like format."""
        if not self.is_custom:
            return response
            
        issues = response.get('issues') or response.get('data') or response.get('results', [])
        
        return {
            'issues': [self._normalize_issue_response(issue) for issue in issues],
            'total': response.get('total') or len(issues),
            'maxResults': response.get('limit') or response.get('max_results', 50),
            'startAt': response.get('offset') or response.get('start_at', 0)
        }

    def _normalize_comment_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API comment response to Jira-like format."""
        if not self.is_custom:
            return response
            
        return {
            'id': response.get('id') or response.get('comment_id'),
            'author': {
                'displayName': response.get('author') or response.get('user') or response.get('created_by', 'Unknown')
            },
            'body': response.get('comment') or response.get('body') or response.get('content'),
            'created': response.get('created') or response.get('created_at'),
            'updated': response.get('updated') or response.get('updated_at')
        }

    def _normalize_project_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API project response to Jira-like format."""
        if not self.is_custom:
            return response
            
        return {
            'key': response.get('key') or response.get('id') or response.get('code'),
            'id': response.get('id') or response.get('project_id'),
            'name': response.get('name') or response.get('title'),
            'description': response.get('description'),
            'lead': response.get('lead') or response.get('owner')
        }

    def _normalize_transition_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API transition response to Jira-like format."""
        if not self.is_custom:
            return response
            
        return {
            'id': response.get('id') or response.get('transition_id'),
            'name': response.get('name') or response.get('status') or response.get('to_status'),
            'to': {
                'name': response.get('to_status') or response.get('target_status')
            }
        }

    def _parse_jql_to_filters(self, jql: str) -> Dict[str, Any]:
        """Convert simple JQL queries to filter parameters for custom API."""
        filters = {}
        
        # Simple parsing - you can extend this based on your API's capabilities
        jql_lower = jql.lower()
        
        if 'project =' in jql_lower:
            # Extract project key
            import re
            match = re.search(r'project\s*=\s*([^\s]+)', jql_lower)
            if match:
                filters['project'] = match.group(1).strip('"\'')
        
        if 'status =' in jql_lower:
            # Extract status
            import re
            match = re.search(r'status\s*=\s*([^\s]+)', jql_lower)
            if match:
                filters['status'] = match.group(1).strip('"\'').replace('"', '')
        
        if 'assignee =' in jql_lower:
            # Extract assignee
            import re
            match = re.search(r'assignee\s*=\s*([^\s]+)', jql_lower)
            if match:
                assignee = match.group(1).strip('"\'')
                if assignee == 'currentuser()':
                    assignee = 'me'  # Assuming your API uses 'me'
                filters['assignee'] = assignee
        
        return filters

    def _transform_issue_data_to_custom(self, project_key: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Jira issue data format to custom API format."""
        custom_data = {
            'project': project_key,
            'title': issue_data.get('summary', ''),
            'description': issue_data.get('description', ''),
            'type': issue_data.get('issue_type', 'Task').lower(),
        }
        
        # Add any custom fields
        if 'custom_fields' in issue_data:
            custom_data.update(issue_data['custom_fields'])
            
        return custom_data

    def _transform_update_data_to_custom(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Jira update data format to custom API format."""
        custom_data = {}
        
        if 'fields' in update_data:
            field_mapping = {
                'summary': 'title',
                'description': 'description',
                'assignee': 'assignee',
                'status': 'status'
            }
            
            for jira_field, custom_field in field_mapping.items():
                if jira_field in update_data['fields']:
                    value = update_data['fields'][jira_field]
                    # Handle nested objects
                    if isinstance(value, dict):
                        if 'name' in value:
                            custom_data[custom_field] = value['name']
                        elif 'displayName' in value:
                            custom_data[custom_field] = value['displayName']
                        else:
                            custom_data[custom_field] = value
                    else:
                        custom_data[custom_field] = value
        
        return custom_data

    # Expose backend methods for direct access
    def get_backend(self):
        """Get the underlying backend integration for direct access."""
        return self.backend

    def is_using_custom_api(self) -> bool:
        """Check if using custom API."""
        return self.is_custom