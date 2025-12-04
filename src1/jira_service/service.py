import logging
from typing import List, Dict, Any
from .client import JiraClient
from .models import JiraIssue, JiraColumn
from config.config_manager import BoardConfig
from core.constants import JiraJsonKeyConstants as JiraJsonKeyConst

logger = logging.getLogger(__name__)

class JiraService:
    def __init__(self, client: JiraClient):
        self.client = client

    def _build_jql_query(self, board, board_config) -> str:
        """Build JQL query for the board"""
        filter_id = board_config.get('filter_id')
        if not filter_id:
            raise ValueError("No filter ID found in board configuration")
            
        base_query = f"filter = {filter_id}"
        
        # Add excluded issue types if specified
        excluded_issue_types = getattr(board, 'jql_exclude_issue_type', None)
        if excluded_issue_types:
            base_query += f" AND issuetype not in ({excluded_issue_types})"
            
        return base_query

    def get_board_issues(self, board: BoardConfig, board_config: Dict[str, Any], additional_fields: List[str] = None) -> List[JiraIssue]:
        """Fetch issues for a specific board"""
        fields = [
            "key", "summary", "status", "created", "updated",
            "resolutiondate", "issuetype", "priority", "resolution",
            "labels", "customfield_10005", "customfield_11115", "components",
            "customfield_12401"  # Correct flag field
        ]
        
        if additional_fields:
            fields.extend(additional_fields)

        # Build JQL query using board filter
        if board.jql:
            jql = board.jql
        else:
            filter_id = board_config['filter_id']
            jql = f"filter = {filter_id}"
            if board.jql_exclude_issue_type:
                jql += f" AND issuetype not in ({board.jql_exclude_issue_type})"

        logger.info(f"Fetching issues for board {board_config['board_name']} with JQL: {jql}")
        raw_issues = self.client.get_issues(
            jql=jql,
            fields=fields,
            expand="changelog"
        )
        logger.info(f"Found {len(raw_issues)} issues for board {board_config['board_name']}")

        return [JiraIssue.from_api_response(issue) for issue in raw_issues]

    def process_issue_status_changes(self, issues: List[JiraIssue], columns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process status changes for all issues"""
        processed_issues = []
        
        # Convert raw column data to JiraColumn objects
        jira_columns = [
            JiraColumn(
                name=col['name'],
                statuses=col['statuses']
            )
            for col in columns
            if col['statuses']  # Only include columns with statuses
        ]
        
        if not jira_columns:
            logger.error("No columns configured for the board")
            return processed_issues

        for issue in issues:
            try:
                issue_data = {"ID": issue.key}
                
                # Initialize all columns with None
                for column in jira_columns:
                    issue_data[column.name] = None
                
                # Get status change dates
                status_dates = issue.get_status_change_dates(jira_columns)
                if status_dates:
                    for column_name, date in status_dates.items():
                        issue_data[column_name] = date
                
                processed_issues.append(issue_data)
                
            except Exception as e:
                logger.error(f"Error processing issue {issue.key}: {str(e)}")
                continue
            
        return processed_issues

    def get_total_issues_count(self, board, board_config) -> int:
        """Get total count of issues for the board"""
        jql = self._build_jql_query(board, board_config)
        return self.client.get_issues_count(jql)

    def get_board_issues(self, board, board_config, progress_callback=None) -> List[JiraIssue]:
        """Get all issues for the board with progress tracking"""
        jql = self._build_jql_query(board, board_config)
        issues = []
        
        # Define required fields
        fields = [
            "key", "summary", "status", "created", "updated",
            "resolutiondate", "issuetype", "priority", "resolution",
            "labels", "customfield_10005", "customfield_11115", "components",
            "customfield_12401"  # Correct flag field
        ]
        
        # Get issues in batches
        start_at = 0
        max_results = 100  # Jira's limit
        
        while True:
            batch = self.client.get_issues(
                jql=jql,
                fields=fields,
                start_at=start_at,
                max_results=max_results,
                expand="changelog"
            )
            if not batch:
                break
            
            # Convert raw issues to JiraIssue objects
            jira_issues = [JiraIssue.from_api_response(issue) for issue in batch]
            issues.extend(jira_issues)
            
            if progress_callback:
                progress_callback(len(batch))
            
            if len(batch) < max_results:
                break
            
            start_at += max_results
        
        return issues