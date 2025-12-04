from typing import Dict, Any, List
import yaml
from pathlib import Path
from core.exceptions import ConfigurationError
from core.constants import ConfigKeyConstants

class BoardConfig:
    def __init__(self, config: Dict[str, Any]):
        self.name = config['name']
        self.board_id = config['board_id']
        self.jql_exclude_issue_type = config.get('jql_exclude_issue_type', '')
        self.show = config.get('show', True)
        self.query_jira_board = config.get('query_jira_board', True)
        self.jql = config.get('jql', '')
        self.columns = config.get('columns', [])

class ConfigManager:
    def __init__(self, main_config_path: str):
        self.main_config_path = Path(main_config_path)
        self.config = self._load_main_config()
        self.boards = self._load_board_config()
        
    def _load_main_config(self) -> Dict[str, Any]:
        """Load and validate main configuration from YAML file"""
        try:
            if not self.main_config_path.exists():
                raise ConfigurationError(f"Config file not found: {self.main_config_path}")
                
            with open(self.main_config_path) as f:
                config = yaml.safe_load(f)
                
            self._validate_main_config(config)
            return config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load main config: {str(e)}")

    def _load_board_config(self) -> List[BoardConfig]:
        """Load JIRA board configuration"""
        try:
            board_config_path = self.main_config_path.parent / self.config['jira_board_config_filename']
            
            if not board_config_path.exists():
                raise ConfigurationError(f"Board config file not found: {board_config_path}")
                
            with open(board_config_path) as f:
                board_data = yaml.safe_load(f)
                
            return [BoardConfig(board) for board in board_data['boards']]
            
        except Exception as e:
            raise ConfigurationError(f"Failed to load board config: {str(e)}")
            
    def _validate_main_config(self, config: Dict[str, Any]) -> None:
        """Validate required configuration fields"""
        required_fields = [
            'jira_url',
            'jira_token_config',
            'jira_board_config_filename'
        ]
        
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            raise ConfigurationError(f"Missing required config fields: {missing_fields}")

    def get_active_boards(self) -> List[BoardConfig]:
        """Get list of boards that should be shown"""
        return [board for board in self.boards if board.show]

    def get_board_by_name(self, name: str) -> BoardConfig:
        """Get board configuration by name"""
        for board in self.boards:
            if board.name == name:
                return board
        raise ConfigurationError(f"Board not found: {name}") 