import requests
from typing import Dict, List, Optional, Any
from ..config import config
import logging

logger = logging.getLogger(__name__)

class ConfluenceIntegration:
    def __init__(self):
        self.base_url = config.confluence.base_url
        self.auth = (config.confluence.username, config.confluence.api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        self.timeout = config.agent.timeout_seconds

    def get_page(self, page_id: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get a Confluence page by ID."""
        if expand is None:
            expand = ['body.storage', 'version']
        
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}"
            params = {'expand': ','.join(expand)}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get page {page_id}: {str(e)}")

    def get_page_by_title(self, space_key: str, title: str, expand: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get a Confluence page by title in a specific space."""
        if expand is None:
            expand = ['body.storage', 'version']
        
        try:
            url = f"{self.base_url}/rest/api/content"
            params = {
                'spaceKey': space_key,
                'title': title,
                'expand': ','.join(expand)
            }
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            results = response.json().get('results', [])
            return results[0] if results else None
        except requests.RequestException as e:
            raise Exception(f"Failed to get page '{title}' in space {space_key}: {str(e)}")

    def search_content(self, cql: str, expand: List[str] = None, limit: int = 25) -> Dict[str, Any]:
        """Search Confluence content using CQL."""
        if expand is None:
            expand = ['body.storage']
        
        try:
            url = f"{self.base_url}/rest/api/content/search"
            params = {
                'cql': cql,
                'expand': ','.join(expand),
                'limit': limit
            }
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to search content: {str(e)}")

    def create_page(self, space_key: str, title: str, content: str, parent_page_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page."""
        try:
            url = f"{self.base_url}/rest/api/content"
            payload = {
                'type': 'page',
                'title': title,
                'space': {'key': space_key},
                'body': {
                    'storage': {
                        'value': content,
                        'representation': 'storage'
                    }
                }
            }
            
            if parent_page_id:
                payload['ancestors'] = [{'id': parent_page_id}]
            
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to create page '{title}': {str(e)}")

    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """Update a Confluence page."""
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}"
            payload = {
                'version': {
                    'number': version + 1
                },
                'title': title,
                'type': 'page',
                'body': {
                    'storage': {
                        'value': content,
                        'representation': 'storage'
                    }
                }
            }
            response = self.session.put(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to update page {page_id}: {str(e)}")

    def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Delete a Confluence page."""
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}"
            response = self.session.delete(url, timeout=self.timeout)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.RequestException as e:
            raise Exception(f"Failed to delete page {page_id}: {str(e)}")

    def get_spaces(self, limit: int = 25) -> Dict[str, Any]:
        """Get all Confluence spaces."""
        try:
            url = f"{self.base_url}/rest/api/space"
            params = {'limit': limit}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get spaces: {str(e)}")

    def get_space(self, space_key: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get a specific Confluence space."""
        if expand is None:
            expand = ['description', 'homepage']
        
        try:
            url = f"{self.base_url}/rest/api/space/{space_key}"
            params = {'expand': ','.join(expand)}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get space {space_key}: {str(e)}")

    def get_page_children(self, page_id: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get child pages of a Confluence page."""
        if expand is None:
            expand = ['body.storage']
        
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}/child/page"
            params = {'expand': ','.join(expand)}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to get children of page {page_id}: {str(e)}")

    def add_comment(self, page_id: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a Confluence page."""
        try:
            url = f"{self.base_url}/rest/api/content"
            payload = {
                'type': 'comment',
                'container': {'id': page_id},
                'body': {
                    'storage': {
                        'value': comment,
                        'representation': 'storage'
                    }
                }
            }
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Failed to add comment to page {page_id}: {str(e)}")

    def get_comments(self, page_id: str) -> List[Dict[str, Any]]:
        """Get comments for a Confluence page."""
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}/child/comment"
            params = {'expand': 'body.storage'}
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('results', [])
        except requests.RequestException as e:
            raise Exception(f"Failed to get comments for page {page_id}: {str(e)}")

    def convert_to_html(self, content: str) -> str:
        """Convert Confluence storage format to HTML."""
        try:
            url = f"{self.base_url}/rest/api/contentbody/convert/storage"
            payload = {
                'value': content,
                'representation': 'storage'
            }
            params = {'to': 'view'}
            response = self.session.post(url, json=payload, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json().get('value', '')
        except requests.RequestException as e:
            raise Exception(f"Failed to convert content to HTML: {str(e)}")