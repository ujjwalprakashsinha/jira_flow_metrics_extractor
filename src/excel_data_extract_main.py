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
from constants import DateUtilConstants as DateUtilConst
from constants import GeneralConstants


def get_config_folder_path() -> str:
    exe_folder = os.path.dirname(__file__)
    return str(os.path.join(os.path.dirname(exe_folder), FileFolderNameConst.CONFIG_FOLDERNAME.value))


def get_output_folder_path() -> str:
    exe_folder = os.path.dirname(__file__)
    return str(os.path.join(os.path.dirname(exe_folder), FileFolderNameConst.OUTPUT_FOLDERNAME.value))


def get_all_active_jira_query_names():
    available_jira_queries = []
    for query in jira_board_queries_config[JiraJsonKeyConst.BOARDS.value]:
        if JiraJsonKeyConst.ACTIVE.value in query and not query[JiraJsonKeyConst.ACTIVE.value]:
            continue
        available_jira_queries.append(query[JiraJsonKeyConst.NAME.value])
    return available_jira_queries


def get_jira_query_by_name(name_of_query):
    for query in jira_board_queries_config[JiraJsonKeyConst.BOARDS.value]:
        if query[JiraJsonKeyConst.NAME.value].casefold() == name_of_query.casefold():
            return query


def get_jira_board_config_by_id(board_id):
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


# ***** The Main code execution starts here ****
try:
    config_file_full_path = os.path.join(get_config_folder_path(), FileFolderNameConst.CONFIG_FILENAME.value)
    with open(config_file_full_path) as file:  # loading config file for this project
        config = json.load(file)
    jira_board_config_full_file_path = os.path.join(get_config_folder_path(),
                                                       config[ConfigKeyConst.JIRA_BOARD_CONFIG_FILENAME.value])
    with open(jira_board_config_full_file_path) as file:  # load jira board query configuration file
        jira_board_queries_config = json.load(file)
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
    if obj_query[JiraJsonKeyConst.QUERY_JIRA_BOARD.value]:
        cur_jira_board_config = get_jira_board_config_by_id(board_id=int(obj_query[JiraJsonKeyConst.BOARD_ID.value]))
        filter_id = cur_jira_board_config[GeneralConstants.FILTER_ID.value]
        if JiraJsonKeyConst.JQL_ISSUE_TYPE.value in obj_query and obj_query[JiraJsonKeyConst.JQL_ISSUE_TYPE.value] != "":
            obj_query[JiraJsonKeyConst.JQL.value] = f"filter = {filter_id} and {obj_query[JiraJsonKeyConst.JQL_ISSUE_TYPE.value]}"
        columns = cur_jira_board_config[GeneralConstants.BOARD_COLUMNS.value]
    else:
        columns = obj_query[JiraJsonKeyConst.COLUMNS.value]
    output_file_name = obj_query[JiraJsonKeyConst.NAME.value] + FileFolderNameConst.COLUMN_OUTPUT_FILE_POSTFIX.value
    obj_jira_data = JiraDataBase(search_query=obj_query[JiraJsonKeyConst.JQL.value], jira_board_columns=columns,
                                 output_file_name=output_file_name)

    print(f'Please wait, we are preparing data for "{obj_query[JiraJsonKeyConst.NAME.value]}"')

    jira = JIRA(options={'server': config[ConfigKeyConst.JIRA_URL_KEY.value]},
                token_auth=jira_token)  # connection to the jira

    search_query = obj_jira_data.search_query  # the search query
    # NEW CODE
    additional_columns = ["summary", "jiralink", "status", "Project Key", "Project Name",  "Story Point"] # customfield_10002 = Story Points
   
    for add_col in additional_columns:
        obj_dict = {}
        obj_dict[JiraJsonKeyConst.COLUMN_NAME.value] = add_col
        obj_jira_data.insert_additional_columns_to_csv(obj_dict)
    # --------
    jira_fields_needed = ["status", "created", "summary", "project", "customfield_10002"] # customfield_10002 = Story Points
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
            # add the change date (needed format) to the csv_row_list object and add to csv
            date_utility = DateUtil(DateUtilConst.DATE_FORMAT_STANDARD.value)
            for column in obj_jira_data.jira_board_columns:
                obj_jira_data.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]] = date_utility.convert_jira_date(
                    obj_jira_data.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]])

            # set additional column values
            obj_jira_data.set_board_column_value("jiralink", f"{config[ConfigKeyConst.JIRA_URL_KEY.value]}/browse/{jira_issue.key}" )
            obj_jira_data.set_board_column_value("status", jira_issue.fields.status)
            obj_jira_data.set_board_column_value("Project Key", jira_issue.fields.project)
            obj_jira_data.set_board_column_value("Project Name", jira_issue.fields.project.name)
            #obj_jira_data.set_board_column_value("Story Point", jira_issue.get_field("customfield_10002") )
            #obj_jira_data.set_board_column_value("summary", jira_issue.fields.summary )
            # write to the object
            csv_writer.writerow(obj_jira_data.csv_single_row_list.values())
    print('\n')
    print(f"Issues fetched: {len(all_jira_issues)} records")
    # if jira_issues.total > 1000:
    #     print('WARNING: This code only fetches top 1000 records returned by the query')
    print(f'CSV file {output_csv_file_fullpath} created...' + ' ' + str(datetime.now()))
except Exception as e:
    print(f"Error : {e}")