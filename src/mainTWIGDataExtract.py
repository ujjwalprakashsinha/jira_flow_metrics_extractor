import csv
from datetime import datetime

from jira import JIRA
import os
import sys
import json
import requests

from credential.credential_manager import CredentialManager
from utils.dateutil import DateUtil
from jira_projects.rawJiraDataBase import JiraDataBase
from constants import JiraJsonKeyConstants as JiraJsonKeyConst
from constants import FileFolderNameConstants as FileFolderNameConst
from constants import ConfigKeyConstants as ConfigKeyConst


def get_config_folder_path() -> str:
    exe_folder = os.path.dirname(__file__)
    return str(os.path.join(os.path.dirname(exe_folder), FileFolderNameConst.CONFIG_FOLDERNAME.value))


def get_output_folder_path() -> str:
    exe_folder = os.path.dirname(__file__)
    return str(os.path.join(os.path.dirname(exe_folder), FileFolderNameConst.OUTPUT_FOLDERNAME.value))


def get_all_active_jira_query_names():
    available_jira_queries = []
    for query in project_queries_config[JiraJsonKeyConst.QUERIES.value]:
        if JiraJsonKeyConst.ACTIVE.value in query and not query[JiraJsonKeyConst.ACTIVE.value]:
            continue
        available_jira_queries.append(query[JiraJsonKeyConst.NAME.value])
    return available_jira_queries


def get_jira_query_by_name(name_of_query):
    for query in project_queries_config[JiraJsonKeyConst.QUERIES.value]:
        if query[JiraJsonKeyConst.NAME.value].casefold() == name_of_query.casefold():
            return query


def get_columns_array_by_board_id(board_id):
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
    return board_columns


# ***** The Main code execution starts here ****
try:
    project_query_config_full_file_path = os.path.join(get_config_folder_path(),
                                                       FileFolderNameConst.PROJECT_QUERY_CONFIG_FILENAME.value)
    with open(project_query_config_full_file_path) as file:  # load jira project query configuration file
        project_queries_config = json.load(file)
    config_file_full_path = os.path.join(get_config_folder_path(), FileFolderNameConst.CONFIG_FILENAME.value)
    with open(config_file_full_path) as file:  # loading config file for this project
        config = json.load(file)
    jira_url = config[ConfigKeyConst.JIRA_URL_KEY.value]
    active_queries = get_all_active_jira_query_names()
    print(f'List of Active Queries in the config are: {active_queries}')
    query_name = input('Write name of a Query to execute (from the above list): ')
    obj_query = get_jira_query_by_name(name_of_query=query_name)
    if obj_query is None:
        print('!!! Invalid Query Name provided. Exiting code !!!')
        sys.exit()

    cred_manager = CredentialManager()
    jira_token = cred_manager.get_credential(config[ConfigKeyConst.JIRA_TOKEN_VARNAME_KEY.value])

    # check for board id, else use the columns from configuration file
    if "board_id" in obj_query and obj_query["board_id"] != "":
        columns = get_columns_array_by_board_id(board_id=int(obj_query["board_id"]))
    else:
        columns = obj_query[JiraJsonKeyConst.COLUMNS.value]
    output_file_name = obj_query[JiraJsonKeyConst.NAME.value] + FileFolderNameConst.OUTPUT_FILE_POSTFIX.value
    obj_jira_data = JiraDataBase(search_query=obj_query[JiraJsonKeyConst.QUERY_TEXT.value], jira_board_columns=columns,
                                 output_file_name=output_file_name)

    print(f'Please wait, we are preparing data for "{obj_query[JiraJsonKeyConst.NAME.value]}"')

    jira = JIRA(options={'server': config[ConfigKeyConst.JIRA_URL_KEY.value]},
                token_auth=jira_token)  # connection to the jira

    search_query = obj_jira_data.search_query  # the search query
    jira_fields_needed = ["status", "created"]
    max_results = 1000 # Maximum results per request (set to JIra's limit)
    all_jira_issues = [] # List to store retrieved issues
    start_at = 0 # Initial starting point for pagination
    while True:
        # Define JQL options with specified fields
        
        jql_options = {"fields": jira_fields_needed}
        jira_issues = jira.search_issues(jql_str=search_query, startAt=start_at,  maxResults=max_results, fields=jira_fields_needed, expand="changelog")
        # Add retrieved issues to the list
        all_jira_issues.extend(jira_issues)
        # print(f"Total Issue count: {jira_issues.total}")
        # Check for more pages
        if len(jira_issues) < max_results:
            break

        # Update starting point for next iteration
        start_at += max_results

    print('Data extracted from Jira...')
    output_folder_path = get_output_folder_path()
    os.makedirs(name=output_folder_path, exist_ok=True)
    output_csv_file_fullpath = os.path.join(output_folder_path, obj_jira_data.file_name)
    with open(output_csv_file_fullpath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        header = obj_jira_data.csv_single_row_list.keys()
        csv_writer.writerow(header)
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
                    if item.field == "status":  # checking for status change in the history
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
            # add the change date (needed format) to the csv_row_list object and add to csv
            date_utility = DateUtil(config[ConfigKeyConst.OUTPUT_DATE_FORMAT_KEY.value])
            for column in obj_jira_data.jira_board_columns:
                obj_jira_data.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]] = date_utility.convert_jira_date(
                    obj_jira_data.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]])

            csv_writer.writerow(obj_jira_data.csv_single_row_list.values())
    print('\n')
    print(f"Issues fetched: {len(all_jira_issues)} records")
    # if jira_issues.total > 1000:
    #     print('WARNING: This code only fetches top 1000 records returned by the query')
    print(f'CSV file {output_csv_file_fullpath} created...' + ' ' + str(datetime.now()))
except Exception as e:
    print(f"Error : {e}")
