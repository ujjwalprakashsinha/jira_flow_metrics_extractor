from typing import List, Dict, Any
import requests
from jira import JIRA
from core.exceptions import JiraExtractorError

class JiraClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.token = token
        # Initialize JIRA client
        self.jira = JIRA(
            server=base_url,
            token_auth=token
        )
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        })

    def get_issues(self, jql: str, fields: List[str], expand: str = None) -> List[Dict[str, Any]]:
        """
        Fetch issues from JIRA with pagination using JIRA SDK
        """
        try:
            all_issues = []
            start_at = 0
            max_results = 100

            while True:
                issues = self.jira.search_issues(
                    jql_str=jql,
                    startAt=start_at,
                    maxResults=max_results,
                    fields=fields,
                    expand=expand
                )
                
                if not issues:
                    break
                    
                all_issues.extend(issues)
                
                if len(issues) < max_results:
                    break
                    
                start_at += max_results

            return all_issues
            
        except Exception as e:
            raise JiraExtractorError(f"Failed to fetch JIRA issues: {str(e)}")

    def get_board_configuration(self, board_id: int) -> Dict[str, Any]:
        """Get board configuration including columns and statuses"""
        try:
            # First get the board details
            board_url = f"{self.base_url}/rest/agile/1.0/board/{board_id}"
            board_response = self.session.get(board_url)
            board_response.raise_for_status()
            board_data = board_response.json()
            
            # Then get the configuration
            config_url = f"{self.base_url}/rest/agile/1.0/board/{board_id}/configuration"
            config_response = self.session.get(config_url)
            config_response.raise_for_status()
            config_data = config_response.json()
            
            columns = []
            for column in config_data['columnConfig']['columns']:
                column_data = {
                    'name': column['name'],
                    'statuses': []
                }
                
                for status in column['statuses']:
                    status_response = self.session.get(status['self'])
                    status_response.raise_for_status()
                    column_data['statuses'].append(status_response.json()['name'])
                    
                columns.append(column_data)
                
            return {
                'board_id': board_id,
                'board_name': board_data['name'],
                'location': board_data.get('location', {}).get('projectName', 'Unknown'),
                'type': board_data.get('type', 'Unknown'),
                'columns': columns,
                'filter_id': config_data['filter']['id']
            }
            
        except Exception as e:
            raise JiraExtractorError(f"Failed to get board configuration: {str(e)}")

    def get_issues_count(self, jql: str) -> int:
        """Get total count of issues matching the JQL query"""
        params = {"jql": jql, "maxResults": 0}
        response = self._get("rest/api/latest/search", params=params)
        return response["total"]

    def get_issues(self, jql: str, fields: List[str], start_at: int = 0, max_results: int = 100, expand: str = None) -> List[Dict]:
        """Get a batch of issues"""
        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": ",".join(fields)
        }
        if expand:
            params["expand"] = expand
        
        response = self._get("rest/api/latest/search", params=params)
        return response["issues"]

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Helper method to make GET requests"""
        response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json() 