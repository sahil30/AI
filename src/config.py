import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class CustomAPIConfig(BaseSettings):
    base_url: str
    api_key: str
    version: str = "v1"
    
    class Config:
        env_prefix = "API_"

class JiraConfig(BaseSettings):
    base_url: Optional[str] = None
    username: Optional[str] = None
    api_token: Optional[str] = None
    
    class Config:
        env_prefix = "JIRA_"

class ConfluenceConfig(BaseSettings):
    base_url: Optional[str] = None
    username: Optional[str] = None
    api_token: Optional[str] = None
    
    class Config:
        env_prefix = "CONFLUENCE_"

class OpenAIConfig(BaseSettings):
    api_key: str
    
    class Config:
        env_prefix = "OPENAI_"

class MCPConfig(BaseSettings):
    enabled: bool = True
    jira_server_path: Optional[str] = None
    confluence_server_path: Optional[str] = None
    timeout_seconds: int = 30
    
    class Config:
        env_prefix = "MCP_"

class AgentConfig(BaseSettings):
    log_level: str = "INFO"
    max_retries: int = 3
    timeout_seconds: int = 30
    use_custom_api: bool = True
    use_mcp_servers: bool = False
    
    class Config:
        env_prefix = ""  # These can come from any prefix

config_instance = None

class Config:
    def __init__(self):
        self.use_custom_api = os.getenv('USE_CUSTOM_API', 'true').lower() == 'true'
        self.use_mcp_servers = os.getenv('USE_MCP_SERVERS', 'false').lower() == 'true'
        
        if self.use_custom_api:
            self.api = CustomAPIConfig()
        
        # Always initialize these for fallback
        self.jira = JiraConfig()
        self.confluence = ConfluenceConfig()
        self.openai = OpenAIConfig()
        self.agent = AgentConfig()
        self.mcp = MCPConfig()
    
    def validate(self):
        # Always require OpenAI API key
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("Missing required environment variable: OPENAI_API_KEY")
        
        if self.use_custom_api:
            # Validate custom API configuration
            required_custom_vars = ['API_BASE_URL', 'API_KEY']
            missing_custom = [var for var in required_custom_vars if not os.getenv(var)]
            
            if missing_custom:
                raise ValueError(f"Missing required custom API variables: {', '.join(missing_custom)}")
        else:
            # Validate standard Atlassian API configuration
            required_atlassian_vars = [
                'JIRA_BASE_URL', 'JIRA_USERNAME', 'JIRA_API_TOKEN',
                'CONFLUENCE_BASE_URL', 'CONFLUENCE_USERNAME', 'CONFLUENCE_API_TOKEN'
            ]
            
            missing_atlassian = [var for var in required_atlassian_vars if not os.getenv(var)]
            
            if missing_atlassian:
                raise ValueError(f"Missing required Atlassian API variables: {', '.join(missing_atlassian)}")

def get_config():
    global config_instance
    if config_instance is None:
        config_instance = Config()
    return config_instance

config = get_config()