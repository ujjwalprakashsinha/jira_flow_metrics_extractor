class JiraExtractorError(Exception):
    """Base exception for the application"""
    pass

class ConfigurationError(JiraExtractorError):
    """Raised when there's an issue with configuration"""
    pass

class CredentialError(JiraExtractorError):
    """Raised when there's an issue with credentials"""
    pass 