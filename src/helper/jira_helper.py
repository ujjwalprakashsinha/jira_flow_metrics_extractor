import os
import json
import requests
from jira import JIRA
from tqdm import tqdm
from constants import JiraJsonKeyConstants as JiraJsonKeyConst, FileFolderNameConstants as FileFolderNameConst, GeneralConstants
from jira_projects.rawJiraDataBase import JiraDataBase

def get_config_file_path(exe_folder_path, file_name) -> str:
    return str(os.path.join(os.path.dirname(exe_folder_path), FileFolderNameConst.CONFIG_FOLDERNAME.value, file_name))


def get_output_folder_path(exe_folder) -> str:
    return str(os.path.join(os.path.dirname(exe_folder), FileFolderNameConst.OUTPUT_FOLDERNAME.value))


def get_all_active_jira_query_names(jira_board_queries_config):
    available_jira_queries = []
    for query in jira_board_queries_config[JiraJsonKeyConst.BOARDS.value]:
        if JiraJsonKeyConst.SHOW.value in query and not query[JiraJsonKeyConst.SHOW.value]:
            continue
        available_jira_queries.append(query[JiraJsonKeyConst.NAME.value])
    return available_jira_queries


def get_jira_query_by_name(name_of_query: str, jira_board_queries_config):
    for query in jira_board_queries_config[JiraJsonKeyConst.BOARDS.value]:
        if query[JiraJsonKeyConst.NAME.value].casefold() == name_of_query.casefold():
            return query


def get_jira_board_config_by_id(board_id: int, jira_token: str, jira_url: str):
    jira_board_config = {}
    board_columns = []
    # Headers with Authorization using API token
    headers = {
        "Authorization": f"Bearer {jira_token}"  # Use Bearer token for API tokens
    }
    # URL for retrieving board configuration
    board_config_url = f"{jira_url}/rest/agile/1.0/board/{board_id}/configuration"
    response = requests.get(board_config_url, headers=headers)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    # Parse JSON response if successful
    board_config = json.loads(response.text)
    for board_column in board_config['columnConfig']['columns']:
        dict_column = {}
        dict_column[JiraJsonKeyConst.COLUMN_NAME.value] = board_column["name"]
        statuses = []
        for status in board_column['statuses']:
            response = requests.get(status['self'], headers=headers)
            response.raise_for_status()  # Raise an exception for non-200 status codes
            jira_status = json.loads(response.text)
            statuses.append(jira_status['name'])
        dict_column[JiraJsonKeyConst.STATUSES.value] = statuses
        board_columns.append(dict_column)
    jira_board_config[GeneralConstants.BOARD_COLUMNS.value] = board_columns
    jira_board_config[GeneralConstants.FILTER_ID.value] = board_config["filter"]["id"]
    jira_board_config[GeneralConstants.BOARD_NAME.value] = board_config["name"]
    return jira_board_config


def get_jira_issues(search_query: str, jira_fields: list, jira_url: str, jira_token: str, issue_history_needed: bool = True)-> list:
    # Headers with Authorization using API token
    headers = {
        "Authorization": f"Bearer {jira_token}"  # Use Bearer token for API tokens
    }
    # URL for retrieving board configuration
    board_config_url = f"{jira_url}/rest/api/2/search"
    params = {"jql": search_query, "maxResults": 0}
    response = requests.get(board_config_url, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    # Parse JSON response if successful
    data = json.loads(response.text)
    # Get the total number of issues matching the query
    total_issues = int(data["total"])
    # Create a progress bar
    progress_bar = tqdm(total=total_issues, unit="issues", desc="Fetching issues")      
    max_results = 100 # Maximum results per request (set to Jira's limit)
    all_jira_issues = [] # List to store retrieved issues
    start_at = 0 # Initial starting point for pagination
    if issue_history_needed:
        expand = "changelog"
    else:
        expand = None
    jira = JIRA(options={'server': jira_url},
                token_auth=jira_token)  # connection to the jira
    while True:
        # Define JQL options with specified fields
        
        jira_issues = jira.search_issues(jql_str=search_query, startAt=start_at,  maxResults=max_results, fields=jira_fields, expand=expand)
        # Update the progress bar
        progress_bar.update(len(jira_issues))
        # Add retrieved issues to the list
        all_jira_issues.extend(jira_issues)
        # Check for more pages
        if len(jira_issues) < max_results:
            break

        # Update starting point for next iteration
        start_at += max_results
    progress_bar.close()
    return all_jira_issues


def log_issue_status_change_history(all_jira_issues: list, obj_jira_data: JiraDataBase):
    for jira_issue in all_jira_issues:
            obj_jira_data.set_row_values_to_blank()
            # assign created date as the value for first column which has mapped status
            # (exclude columns with no mapped status on jira board like backlog in Kanban board sometime)
            obj_jira_data.csv_single_row_list[obj_jira_data.get_first_column_having_mapped_status()] = jira_issue.fields.created
            obj_jira_data.set_issue_id(jira_issue.key)
            mapped_column_final_issue_status = obj_jira_data.get_mapped_column_for_status(
                current_status=jira_issue.fields.status.name)
            for history in jira_issue.changelog.histories:
                for item in history.items:
                    if item.field == "status" and item.toString != item.fromString :  # checking for status change in the history & that status did not change to same
                        mapped_column_current_issue_status = obj_jira_data.get_mapped_column_for_status(
                            current_status=item.toString)
                        if mapped_column_current_issue_status == '' or mapped_column_current_issue_status is None:
                            print(f'Info: Status mapping missing for: {item.toString} | Issue ID: {obj_jira_data.csv_single_row_list[JiraDataBase._idColumnName]} | Change Date: {history.created}')
                            break

                        obj_jira_data.set_board_column_value(mapped_column_for_status=mapped_column_current_issue_status,
                                                       status_change_date=history.created)
                        obj_jira_data.clear_later_workflow_column_value(
                            mapped_column_for_status=mapped_column_current_issue_status)

            obj_jira_data.clear_later_workflow_column_value(mapped_column_final_issue_status)