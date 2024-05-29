import os
import json
import requests
from constants import JiraJsonKeyConstants as JiraJsonKeyConst, FileFolderNameConstants as FileFolderNameConst, GeneralConstants

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


def get_jira_query_by_name(name_of_query, jira_board_queries_config):
    for query in jira_board_queries_config[JiraJsonKeyConst.BOARDS.value]:
        if query[JiraJsonKeyConst.NAME.value].casefold() == name_of_query.casefold():
            return query


def get_jira_board_config_by_id(board_id, jira_token, jira_url):
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