from typing import Dict, List, Optional, Any
from ..config import config
from .confluence_integration import ConfluenceIntegration
from .custom_api import CustomAPIIntegration
import logging

logger = logging.getLogger(__name__)

class AdaptiveConfluenceIntegration:
    """
    Adaptive Confluence integration that can work with either standard Atlassian Confluence API
    or your custom API that provides document/wiki-like functionality.
    """
    
    def __init__(self):
        if config.use_custom_api:
            self.backend = CustomAPIIntegration()
            self.is_custom = True
            logger.info("Using custom API for Confluence operations")
        else:
            self.backend = ConfluenceIntegration()
            self.is_custom = False
            logger.info("Using standard Atlassian Confluence API")

    def get_page(self, page_id: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get a Confluence page by ID."""
        if self.is_custom:
            response = self.backend.get_page(page_id, expand)
            return self._normalize_page_response(response)
        else:
            return self.backend.get_page(page_id, expand)

    def get_page_by_title(self, space_key: str, title: str, expand: List[str] = None) -> Optional[Dict[str, Any]]:
        """Get a Confluence page by title in a specific space."""
        if self.is_custom:
            # Use search functionality to find page by title
            search_results = self.backend.search_pages(query=title, space_id=space_key, limit=1)
            pages = search_results.get('pages') or search_results.get('data') or search_results.get('results', [])
            
            if pages:
                page = pages[0]
                # Check if title matches exactly (case-insensitive)
                page_title = page.get('title') or page.get('name', '').lower()
                if page_title.lower() == title.lower():
                    return self._normalize_page_response(page)
            return None
        else:
            return self.backend.get_page_by_title(space_key, title, expand)

    def search_content(self, query: str, expand: List[str] = None, limit: int = 25) -> Dict[str, Any]:
        """Search Confluence content."""
        if self.is_custom:
            # Convert CQL-like query to simple search
            simple_query = self._parse_cql_to_simple_query(query)
            response = self.backend.search_pages(simple_query, limit=limit)
            return self._normalize_search_response(response)
        else:
            return self.backend.search_content(query, expand, limit)

    def create_page(self, space_key: str, title: str, content: str, parent_page_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new Confluence page."""
        if self.is_custom:
            page_data = self._transform_page_data_to_custom(space_key, title, content, parent_page_id)
            response = self.backend.create_page(page_data)
            return self._normalize_page_response(response)
        else:
            return self.backend.create_page(space_key, title, content, parent_page_id)

    def update_page(self, page_id: str, title: str, content: str, version: int) -> Dict[str, Any]:
        """Update a Confluence page."""
        if self.is_custom:
            page_data = {
                'title': title,
                'content': content,
                'version': version + 1
            }
            response = self.backend.update_page(page_id, page_data)
            return self._normalize_page_response(response)
        else:
            return self.backend.update_page(page_id, title, content, version)

    def delete_page(self, page_id: str) -> Dict[str, Any]:
        """Delete a Confluence page."""
        if self.is_custom:
            return self.backend.delete_page(page_id)
        else:
            return self.backend.delete_page(page_id)

    def get_spaces(self, limit: int = 25) -> Dict[str, Any]:
        """Get all Confluence spaces."""
        if self.is_custom:
            spaces = self.backend.get_spaces(limit)
            return {
                'results': [self._normalize_space_response(space) for space in spaces],
                'size': len(spaces),
                'limit': limit
            }
        else:
            return self.backend.get_spaces(limit)

    def get_space(self, space_key: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get a specific Confluence space."""
        if self.is_custom:
            # Try to find space in the list of all spaces
            spaces = self.backend.get_spaces()
            for space in spaces:
                if space.get('key') == space_key or space.get('id') == space_key:
                    return self._normalize_space_response(space)
            raise Exception(f"Space {space_key} not found")
        else:
            return self.backend.get_space(space_key, expand)

    def get_page_children(self, page_id: str, expand: List[str] = None) -> Dict[str, Any]:
        """Get child pages of a Confluence page."""
        if self.is_custom:
            # Custom API might not have hierarchical pages, so search for pages with parent reference
            try:
                # Try a generic approach - this depends on your API structure
                response = self.backend.get(f'/pages/{page_id}/children')
                children = response.get('children') or response.get('data', [])
                return {
                    'results': [self._normalize_page_response(child) for child in children],
                    'size': len(children)
                }
            except Exception:
                # Fallback - return empty children
                return {'results': [], 'size': 0}
        else:
            return self.backend.get_page_children(page_id, expand)

    def add_comment(self, page_id: str, comment: str) -> Dict[str, Any]:
        """Add a comment to a Confluence page."""
        if self.is_custom:
            response = self.backend.add_comment(page_id, comment)
            return self._normalize_comment_response(response)
        else:
            return self.backend.add_comment(page_id, comment)

    def get_comments(self, page_id: str) -> List[Dict[str, Any]]:
        """Get comments for a Confluence page."""
        if self.is_custom:
            # Adapt to custom API comment structure
            try:
                comments = self.backend.get_comments(page_id)
                return [self._normalize_comment_response(comment) for comment in comments]
            except Exception:
                # Some custom APIs might not support comments on pages
                return []
        else:
            return self.backend.get_comments(page_id)

    def convert_to_html(self, content: str) -> str:
        """Convert content to HTML."""
        if self.is_custom:
            # Custom API might not support content conversion
            # Return as-is or apply simple markdown-to-HTML if needed
            return content
        else:
            return self.backend.convert_to_html(content)

    # Normalization methods for custom API responses
    def _normalize_page_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API page response to Confluence-like format."""
        if not self.is_custom:
            return response
            
        normalized = {
            'id': response.get('id') or response.get('page_id'),
            'title': response.get('title') or response.get('name'),
            'type': 'page',
            'status': response.get('status', 'current')
        }
        
        # Handle content/body
        content = response.get('content') or response.get('body') or response.get('text', '')
        normalized['body'] = {
            'storage': {
                'value': content,
                'representation': 'storage'
            },
            'view': {
                'value': content,  # Assume content is already viewable
                'representation': 'view'
            }
        }
        
        # Handle space
        space = response.get('space') or response.get('space_key') or response.get('namespace')
        if space:
            if isinstance(space, dict):
                normalized['space'] = space
            else:
                normalized['space'] = {'key': space, 'name': space}
        
        # Handle version
        normalized['version'] = {
            'number': response.get('version') or response.get('revision', 1),
            'when': response.get('updated') or response.get('updated_at'),
            'by': {
                'displayName': response.get('updated_by') or response.get('author', 'Unknown')
            }
        }
        
        # Handle creation info
        normalized['history'] = {
            'createdDate': response.get('created') or response.get('created_at'),
            'createdBy': {
                'displayName': response.get('created_by') or response.get('author', 'Unknown')
            }
        }
        
        # Handle links if available
        if response.get('url') or response.get('link'):
            normalized['_links'] = {
                'webui': response.get('url') or response.get('link'),
                'self': f"/rest/api/content/{normalized['id']}"
            }
            
        return normalized

    def _normalize_search_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API search response to Confluence-like format."""
        if not self.is_custom:
            return response
            
        pages = response.get('pages') or response.get('data') or response.get('results', [])
        
        return {
            'results': [self._normalize_page_response(page) for page in pages],
            'size': len(pages),
            'limit': response.get('limit') or 25,
            'start': response.get('offset') or response.get('start', 0)
        }

    def _normalize_space_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API space response to Confluence-like format."""
        if not self.is_custom:
            return response
            
        return {
            'key': response.get('key') or response.get('id') or response.get('code'),
            'name': response.get('name') or response.get('title'),
            'description': {
                'plain': {
                    'value': response.get('description', ''),
                    'representation': 'plain'
                }
            },
            'type': response.get('type', 'global'),
            '_links': {
                'webui': response.get('url') or response.get('link', ''),
                'self': f"/rest/api/space/{response.get('key') or response.get('id')}"
            }
        }

    def _normalize_comment_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize custom API comment response to Confluence-like format."""
        if not self.is_custom:
            return response
            
        return {
            'id': response.get('id') or response.get('comment_id'),
            'type': 'comment',
            'title': response.get('title', ''),
            'body': {
                'storage': {
                    'value': response.get('comment') or response.get('body') or response.get('content', ''),
                    'representation': 'storage'
                }
            },
            'version': {
                'number': response.get('version', 1),
                'when': response.get('created') or response.get('created_at'),
                'by': {
                    'displayName': response.get('author') or response.get('user') or response.get('created_by', 'Unknown')
                }
            }
        }

    def _parse_cql_to_simple_query(self, cql: str) -> str:
        """Convert simple CQL queries to basic search terms."""
        # Simple parsing - extract key search terms
        import re
        
        # Remove CQL operators and extract search terms
        cql = re.sub(r'\b(and|or|not)\b', ' ', cql, flags=re.IGNORECASE)
        cql = re.sub(r'(space|type|title|text)\s*=\s*["\']?([^"\']+)["\']?', r'\2', cql, flags=re.IGNORECASE)
        
        # Clean up and return
        return ' '.join(cql.split())

    def _transform_page_data_to_custom(self, space_key: str, title: str, content: str, parent_page_id: Optional[str] = None) -> Dict[str, Any]:
        """Transform Confluence page data format to custom API format."""
        page_data = {
            'title': title,
            'content': content,
            'space': space_key,
        }
        
        if parent_page_id:
            page_data['parent_id'] = parent_page_id
            
        return page_data

    # Expose backend methods for direct access
    def get_backend(self):
        """Get the underlying backend integration for direct access."""
        return self.backend

    def is_using_custom_api(self) -> bool:
        """Check if using custom API."""
        return self.is_custom