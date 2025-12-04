from typing import Dict
import os
from core.exceptions import CredentialError
from core.constants import ConfigKeyConstants

class CredentialManager:
    @staticmethod
    def get_credential(token_config: Dict[str, str]) -> str:
        """
        Get credentials from environment or config
        
        Args:
            token_config: Dictionary containing token configuration
                Expected format: {
                    "mode": "env_var|string",
                    "value": "JIRA_TOKEN or actual_token"
                }
        
        Returns:
            str: The credential value
            
        Raises:
            CredentialError: If credential cannot be retrieved
        """
        try:
            mode = token_config.get(ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_KEY.value)
            value = token_config.get(ConfigKeyConstants.JIRA_TOKEN_CONFIG_VALUE_KEY.value)

            if not mode or not value:
                raise CredentialError("Missing required token configuration fields")

            if mode == ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_ENV_VAR.value:
                credential = os.environ.get(value)
                if not credential:
                    raise CredentialError(f"Environment variable '{value}' not found or empty")
                return credential
            
            elif mode == ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_STRING.value:
                return value
            
            raise CredentialError(f"Invalid credential mode: {mode}")
            
        except Exception as e:
            raise CredentialError(f"Failed to get credentials: {str(e)}") 