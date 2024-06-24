import os
import json
import requests
from jira import JIRA
from tqdm import tqdm
from helper.constants import JiraJsonKeyConstants as JiraJsonKeyConst, FileFolderNameConstants as FileFolderNameConst, GeneralConstants as GeneralConst

class JiraWorkItem:

    def __init__(self, search_query, jira_board_columns, output_file_name):
        self.file_name: str = output_file_name
        self.search_query: str = search_query
        self.jira_board_columns = jira_board_columns
        self.csv_single_row_list = {
            GeneralConst.ID_COLUMN_NAME.value: 0
        }

        # Build the row_list using the columns array
        temp_columns = self.jira_board_columns.copy()
        for column in temp_columns:
            if JiraJsonKeyConst.STATUSES.value in column and len(column[JiraJsonKeyConst.STATUSES.value]) == 0:
                self.jira_board_columns.remove(column)

        for column in self.jira_board_columns:
            self.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]] = ''

    def insert_additional_columns_to_csv(self, additional_columns):
        for column in additional_columns:
            if column != None:
                obj_dict = {}
                obj_dict[JiraJsonKeyConst.COLUMN_NAME.value] = column
                self.csv_single_row_list[obj_dict[JiraJsonKeyConst.COLUMN_NAME.value]] = ''

    def clear_later_workflow_column_value(self, mapped_column_for_status):
        found: bool = False
        for value in self.csv_single_row_list:
            if value == mapped_column_for_status:
                found = True
                continue
            if found:
                self.csv_single_row_list[value] = ''

    def set_issue_id(self, issue_id):
        self.csv_single_row_list[GeneralConst.ID_COLUMN_NAME.value] = issue_id

    
    def set_value_for_csvcolumn(self, mapped_csvcolumn_for_field, new_value):
        if mapped_csvcolumn_for_field:
            self.csv_single_row_list[mapped_csvcolumn_for_field] = new_value

    def set_row_values_to_blank(self):
        for columns in self.csv_single_row_list:
            self.csv_single_row_list[columns] = ''
    
    def get_mapped_csvcolumn_for_status(self, current_status: str) -> str:
        mapped_column: str = ''
        loop_breaker = False
        for column in self.jira_board_columns:
            for status in column[JiraJsonKeyConst.STATUSES.value]:
                if current_status != None and status.casefold() == current_status.casefold():
                    mapped_column = column[JiraJsonKeyConst.COLUMN_NAME.value]
                    loop_breaker = True
                    break
            if loop_breaker:
                break
        return mapped_column

    def get_first_column_having_mapped_status(self):
        first_column_with_mapped_status: str = ""
        for jira_column in self.jira_board_columns:
            if len(jira_column)>0:
                first_column_with_mapped_status = jira_column[JiraJsonKeyConst.COLUMN_NAME.value]
                break
        
        return first_column_with_mapped_status


def get_all_active_jira_query_names(jira_board_queries_config) -> list:
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


def get_jira_service_response(service_url, jira_token, service_params=None):
    # Headers with Authorization using API token
    headers = {
        "Authorization": f"Bearer {jira_token}"  # Use Bearer token for API tokens
    }
    # URL for retrieving board configuration
    response = requests.get(service_url, headers=headers, params=service_params)
    response.raise_for_status()  # Raise an exception for non-200 status codes
    # Parse JSON response if successful
    return json.loads(response.text)

def get_jira_board_config_by_id(board_id: int, jira_token: str, jira_url: str):
    jira_board_config = {}
    board_columns = []
    
    board_config_service_url = f"{jira_url}/rest/agile/1.0/board/{board_id}/configuration"
    
    board_config = get_jira_service_response(service_url=board_config_service_url, jira_token=jira_token)
    for board_column in board_config['columnConfig']['columns']:
        dict_column = {}
        dict_column[JiraJsonKeyConst.COLUMN_NAME.value] = board_column["name"]
        statuses = []
        for status in board_column['statuses']:
            jira_status = get_jira_service_response(service_url=status['self'], jira_token=jira_token)
            statuses.append(jira_status['name'])
        dict_column[JiraJsonKeyConst.STATUSES.value] = statuses
        board_columns.append(dict_column)
    jira_board_config[GeneralConst.BOARD_COLUMNS.value] = board_columns
    jira_board_config[GeneralConst.FILTER_ID.value] = board_config["filter"]["id"]
    jira_board_config[GeneralConst.BOARD_NAME.value] = board_config["name"]
    return jira_board_config


def get_jira_issues(search_query: str, jira_fields: list, jira_url: str, jira_token: str, issue_history_needed: bool = True)-> list:
    
    jira_issue_search_service_url = f"{jira_url}/rest/api/2/search"
    params = {"jql": search_query, "maxResults": 0}
    data = get_jira_service_response(jira_issue_search_service_url, jira_token=jira_token, service_params=params)
    
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


def log_issue_status_change_history(all_jira_issues: list, obj_jira_data: JiraWorkItem):
    for jira_issue in all_jira_issues:
            obj_jira_data.set_row_values_to_blank()
            # assign created date as the value for first column which has mapped status
            # (exclude columns with no mapped status on jira board like backlog in Kanban board sometime)
            obj_jira_data.csv_single_row_list[obj_jira_data.get_first_column_having_mapped_status()] = jira_issue.fields.created
            obj_jira_data.set_issue_id(jira_issue.key)
            mapped_column_final_issue_status = obj_jira_data.get_mapped_csvcolumn_for_status(
                current_status=jira_issue.fields.status.name)
            for history in jira_issue.changelog.histories:
                for item in history.items:
                    if item.field == "status" and item.toString != item.fromString :  # checking for status change in the history & that status did not change to same
                        mapped_column_current_issue_status = obj_jira_data.get_mapped_csvcolumn_for_status(
                            current_status=item.toString)
                        if mapped_column_current_issue_status == '' or mapped_column_current_issue_status is None:
                            print(f'Info: Status mapping missing for: {item.toString} | Issue ID: {obj_jira_data.csv_single_row_list[GeneralConst.ID_COLUMN_NAME.value]} | Change Date: {history.created}')
                            break

                        obj_jira_data.set_value_for_csvcolumn(mapped_csvcolumn_for_field=mapped_column_current_issue_status,
                                                       new_value=history.created)
                        obj_jira_data.clear_later_workflow_column_value(
                            mapped_column_for_status=mapped_column_current_issue_status)

            obj_jira_data.clear_later_workflow_column_value(mapped_column_final_issue_status)