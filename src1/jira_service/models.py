from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from jira.resources import Issue
import logging

logger = logging.getLogger(__name__)

@dataclass
class JiraColumn:
    name: str
    statuses: List[str]

@dataclass
class JiraIssue:
    key: str
    summary: str
    status: str
    created_date: datetime
    updated_date: datetime
    changelog: List[Dict[str, Any]]
    resolution_date: Optional[datetime] = None
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    resolution: Optional[str] = None
    labels: Optional[List[str]] = None
    epic_link: Optional[str] = None
    environment: Optional[str] = None
    components: Optional[List[str]] = None
    flagged: bool = False

    def __init__(
        self,
        key: str,
        summary: str,
        status: str,
        issue_type: str,
        priority: str,
        resolution: Optional[str],
        labels: List[str],
        epic_link: Optional[str],
        environment: Optional[str],
        components: List[str],
        flagged: bool,
        created: datetime,
        changelog: List[Dict[str, Any]]
    ):
        self.key = key
        self.summary = summary
        self.status = status
        self.issue_type = issue_type
        self.priority = priority
        self.resolution = resolution
        self.labels = labels
        self.epic_link = epic_link
        self.environment = environment
        self.components = components
        self.flagged = flagged
        self.created = created
        self.changelog = changelog

    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'JiraIssue':
        """Create a JiraIssue instance from JIRA API response"""
        fields = data.get('fields', {})
        
        return cls(
            key=data.get('key'),
            summary=fields.get('summary'),
            status=fields.get('status', {}).get('name'),
            issue_type=fields.get('issuetype', {}).get('name'),
            priority=fields.get('priority', {}).get('name'),
            resolution=fields.get('resolution', {}).get('name') if fields.get('resolution') else None,
            labels=fields.get('labels', []),
            epic_link=fields.get('customfield_10005'),  # Epic Link field
            environment=fields.get('customfield_11115'),  # Environment field
            components=[c.get('name') for c in fields.get('components', [])],
            flagged=bool(fields.get('customfield_12401')),  # Flag field
            created=fields.get('created'),
            changelog=data.get('changelog', {}).get('histories', [])
        )

    def get_mapped_column_for_status(self, status: str, columns: List[JiraColumn]) -> Optional[str]:
        """Get the column name for a given status"""
        for column in columns:
            if any(s.casefold() == status.casefold() for s in column.statuses):
                return column.name
        return None

    def get_first_column_with_status(self, columns: List[JiraColumn]) -> Optional[str]:
        """Get the first column that has mapped statuses"""
        for column in columns:
            if column.statuses:
                return column.name
        return None

    def get_status_change_dates(self, columns: List[JiraColumn]) -> Dict[str, Optional[datetime]]:
        """Get the dates when the issue entered each column's status"""
        status_dates = {column.name: None for column in columns}
        
        # Set creation date for the first column
        if columns:
            first_column = columns[0]
            status_dates[first_column.name] = self.created
            logger.debug(f"Set created date {self.created} for first column {first_column.name} in issue {self.key}")
        
        # Process changelog in chronological order
        for change in sorted(self.changelog, key=lambda x: x['created']):
            new_status = change['toString']
            
            # Find matching column for the new status
            for column in columns:
                if any(s.casefold() == new_status.casefold() for s in column.statuses):
                    status_dates[column.name] = change['created']
                    
                    # Clear later columns
                    found_current = False
                    for col in columns:
                        if col.name == column.name:
                            found_current = True
                        elif found_current:
                            status_dates[col.name] = None
                    break
        
        return status_dates 