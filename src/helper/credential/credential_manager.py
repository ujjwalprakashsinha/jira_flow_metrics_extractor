import os 
from helper.constants import ConfigKeyConstants

class CredentialManager:

    @staticmethod
    def get_credential(token_config):
        if token_config.get(ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_KEY.value) == ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_ENV_VAR.value:
            env_var_name = token_config.get(ConfigKeyConstants.JIRA_TOKEN_CONFIG_VALUE_KEY.value)
            credential_value = os.environ.get(env_var_name)
            if not credential_value:
                raise Exception(f"The provided credential in the environment variable '{env_var_name}' is either empty or does not exists")
            return credential_value
        elif token_config.get(ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_KEY.value) == ConfigKeyConstants.JIRA_TOKEN_CONFIG_MODE_STRING.value:
            return token_config.get(ConfigKeyConstants.JIRA_TOKEN_CONFIG_VALUE_KEY.value)
        else:
            raise Exception("Jira credential info not correctly provided, please check for configuration settings")