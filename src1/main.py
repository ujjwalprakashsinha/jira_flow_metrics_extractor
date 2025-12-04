import logging
import sys
from pathlib import Path
import pandas as pd
import re
from typing import Dict, List, Any
from tqdm import tqdm

from config.config_manager import ConfigManager
from jira_service.client import JiraClient
from jira_service.service import JiraService
from utils.credential import CredentialManager
from core.constants import FileFolderNameConstants
from jira_service.models import JiraIssue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def select_board(config_manager: ConfigManager) -> Dict[str, Any]:
    """Interactive board selection"""
    active_boards = config_manager.get_active_boards()
    print('-----------------------------------------')
    print('List of Active Boards in the config are:')
    print('-----------------------------------------')
    for index, board in enumerate(active_boards):
        print(f"{index}. {board.name}")
    print('-----------------------------------------')
    
    input_index = int(input('Type the number for the option (from the above list): '))
    if input_index < 0 or input_index >= len(active_boards):
        raise ValueError("Invalid board selection index")
    
    return active_boards[input_index]

def print_board_info(board_config: Dict[str, Any], excluded_issue_types: str = None):
    """Print board information"""
    print("---------------------------------------")
    print(f"Jira Board name: \n \t{board_config['board_name']}")
    print(f"Board ID: \n \t{board_config['board_id']}")
    if excluded_issue_types:
        print(f"Excluded Issue Type/s: \n \t{excluded_issue_types}")
    print("---------------------------------------")

def prepare_output_paths(script_path: Path, board_name: str) -> Dict[str, Path]:
    """Prepare output file paths"""
    output_dir = script_path.parent / FileFolderNameConstants.OUTPUT_FOLDERNAME.value
    output_dir.mkdir(exist_ok=True)
    
    return {
        "flow_metrics": output_dir / f"{board_name}{FileFolderNameConstants.FM_OUTPUT_FILE_POSTFIX.value}{FileFolderNameConstants.CSV_FILE_EXTENSION.value}",
        "merged": output_dir / f"{board_name}{FileFolderNameConstants.MERGED_OUTPUT_FILE_POSTFIX.value}{FileFolderNameConstants.CSV_FILE_EXTENSION.value}"
    }

def process_additional_fields(issues: List[JiraIssue], jira_url: str) -> pd.DataFrame:
    """Process additional fields for issues"""
    additional_fields = []
    
    print('Processing additional fields...')
    for issue in tqdm(issues, desc="Processing issues"):
        field_data = {
            "ID": issue.key,
            "Title": issue.summary,
            "Status": issue.status,
            "Type": issue.issue_type,
            "Priority": issue.priority,
            "Resolution": issue.resolution,
            "Labels": ', '.join(issue.labels) if issue.labels else None,
            "Epic Link": issue.epic_link,
            "Environment": issue.environment,
            "Components": ', '.join(issue.components) if issue.components else None,
            "Flagged": "true" if issue.flagged else "false",
            "Link": f"{jira_url}/browse/{issue.key}"
        }
        additional_fields.append(field_data)
    
    df = pd.DataFrame(additional_fields)
    
    # Ensure column order
    columns = [
        "ID", "Link", "Title", "Status", "Type", "Priority", 
        "Resolution", "Labels", "Epic Link", "Environment", 
        "Components", "Flagged"
    ]
    
    # Reorder columns and ensure all columns exist
    existing_columns = [col for col in columns if col in df.columns]
    df = df[existing_columns]
    
    return df

def replace_commas_in_list_of_strings(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Replace commas in list values with pipe separator within square brackets"""
    if column_name in df.columns:
        df[column_name] = df[column_name].apply(
            lambda x: f"[{' | '.join(x.split(','))}]" if isinstance(x, str) else x
        )
    return df

def process_merged_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Process the merged dataframe"""
    # Handle comma-separated values
    if "Labels" in df.columns:
        df = replace_commas_in_list_of_strings(df, 'Labels')
    if "Components" in df.columns:
        df = replace_commas_in_list_of_strings(df, 'Components')
    
    # Clean text fields
    if "Title" in df.columns:
        df['Title'] = df['Title'].apply(lambda x: re.sub(r'[^\w\s]', '', str(x)))
    
    # Reorder columns
    first_cols = ['ID', 'Link', 'Flagged']
    remaining_cols = [col for col in df.columns if col not in first_cols]
    df = df[first_cols + remaining_cols]
    
    return df

def main():
    try:
        # Load configuration
        config_manager = ConfigManager("configs/config.yaml")
        config = config_manager.config
        
        # Select board interactively
        board = select_board(config_manager)
        
        # Setup JIRA client and service
        token = CredentialManager.get_credential(config["jira_token_config"])
        jira_client = JiraClient(config["jira_url"], token)
        jira_service = JiraService(jira_client)
        
        # Get board configuration and display info
        board_config = jira_client.get_board_configuration(board.board_id)
        print_board_info(
            board_config, 
            board.jql_exclude_issue_type if hasattr(board, 'jql_exclude_issue_type') else None
        )
        
        # Prepare output paths
        script_path = Path(__file__).resolve()
        file_paths = prepare_output_paths(script_path, board.name)
        
        print(f'Please wait, preparing data for "{board.name}"')
        
        # Get issues and process them
        print('Fetching issues from JIRA...')
        # First get total count
        total_issues = jira_service.get_total_issues_count(board, board_config)
        print(f"Found {total_issues} issues")
        
        # Create progress bar for fetching
        progress_bar = tqdm(total=total_issues, unit="issues", desc="Fetching issues")
        issues = jira_service.get_board_issues(board, board_config, progress_callback=progress_bar.update)
        progress_bar.close()
        
        # Process status changes
        print('Extracting status change information...')
        flow_metrics_data = []
        progress_bar = tqdm(total=len(issues), unit="issues", desc="Processing status changes")
        for issue in issues:
            metrics = jira_service.process_issue_status_changes([issue], board_config['columns'])
            flow_metrics_data.extend(metrics)
            progress_bar.update(1)
        progress_bar.close()
        flow_metrics_df = pd.DataFrame(flow_metrics_data)
        
        # Process additional fields
        additional_fields_df = process_additional_fields(issues, config["jira_url"])
        
        print('Merging datasets...')
        merged_df = pd.merge(
            flow_metrics_df, 
            additional_fields_df, 
            on="ID", 
            how='inner'
        )
        merged_df = process_merged_dataframe(merged_df)
        
        # Save outputs
        print('Saving output files...')
        flow_metrics_df.to_csv(file_paths["flow_metrics"], index=False)
        merged_df.to_csv(file_paths["merged"], index=False)
        
        print("\nOutput Files:")
        for name, path in file_paths.items():
            print(f"\t{path}")
        
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 