import requests
from typing import Dict, List, Optional, Any
from ..config import config
import logging

logger = logging.getLogger(__name__)

class JiraIntegration:
    def __init__(self):
        self.base_url = config.jira.base_url
        self.auth = (config.jira.username, config.jira.api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.timeout = config.agent.timeout_seconds

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get a specific Jira issue by key."""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get issue {issue_key}: {str(e)}")

    def search_issues(self, jql: str, fields: List[str] = None) -> Dict[str, Any]:
        """Search for Jira issues using JQL."""
        if fields is None:
            fields = ['summary', 'status', 'assignee', 'created']
        
        try:
            url = f"{self.base_url}/rest/api/3/search"
            payload = {
                'jql': jql,
                'fields': fields,
                'maxResults': 100
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to search issues: {str(e)}")

    def create_issue(self, project_key: str, issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Jira issue."""
        try:
            url = f"{self.base_url}/rest/api/3/issue"
            payload = {
                'fields': {
                    'project': {'key': project_key},
                    'summary': issue_data['summary'],
                    'description': {
                        'type': 'doc',
                        'version': 1,
                        'content': [{
                            'type': 'paragraph',
                            'content': [{'type': 'text', 'text': issue_data.get('description', '')}]
                        }]
                    },
                    'issuetype': {'name': issue_data.get('issue_type', 'Task')},
                    **issue_data.get('custom_fields', {})
                }
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to create issue: {str(e)}")

    def update_issue(self, issue_key: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira issue."""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
            payload = {
                'fields': update_data.get('fields', {}),
                'update': update_data.get('update', {})
            }
            response = self.session.put(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.RequestException as e:
            raise Exception(f"Failed to update issue {issue_key}: {str(e)}")

    def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a Jira issue."""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
            payload = {
                'body': {
                    'type': 'doc',
                    'version': 1,
                    'content': [{
                        'type': 'paragraph',
                        'content': [{'type': 'text', 'text': comment}]
                    }]
                }
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to add comment to {issue_key}: {str(e)}")

    def get_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get comments for a Jira issue."""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('comments', [])
        except requests.RequestException as e:
            raise Exception(f"Failed to get comments for {issue_key}: {str(e)}")

    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        try:
            url = f"{self.base_url}/rest/api/3/project"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get projects: {str(e)}")

    def transition_issue(self, issue_key: str, transition_id: str) -> Dict[str, Any]:
        """Transition a Jira issue."""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
            payload = {
                'transition': {'id': transition_id}
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.RequestException as e:
            raise Exception(f"Failed to transition issue {issue_key}: {str(e)}")

    def get_transitions(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get available transitions for a Jira issue."""
        try:
            url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('transitions', [])
        except requests.RequestException as e:
            raise Exception(f"Failed to get transitions for {issue_key}: {str(e)}")