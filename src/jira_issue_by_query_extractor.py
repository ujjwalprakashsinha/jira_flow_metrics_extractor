import csv
from datetime import datetime

import os
import yaml
from credential.credential_manager import CredentialManager
from constants import FileFolderNameConstants as FileFolderNameConst
from constants import ConfigKeyConstants as ConfigKeyConst
import helper.jira_helper as jira_helper

# ***** The Main code execution starts here ****
try:
    exe_path = os.path.dirname(__file__)
    config_file_full_path = jira_helper.get_config_file_path(exe_path, FileFolderNameConst.CONFIG_FILENAME.value)
    with open(config_file_full_path) as file:  # loading config file for this project
        config = yaml.safe_load(file)
    jira_url = config[ConfigKeyConst.JIRA_URL_KEY.value]
    
    cred_manager = CredentialManager()
    jira_token = cred_manager.get_credential(config[ConfigKeyConst.JIRA_TOKEN_VARNAME_KEY.value])
    output_file_name = "Six_Bug_Raw_Data.csv" 
    
    search_query = "issuetype = Bug and statusCategory in ('To Do', 'In Progress')" # the search query
    #search_query = "filter = 27620 AND resolutiondate >= -300d AND resolutiondate >= 2024-06-02 AND resolutiondate < 2024-06-09" # the search query

    jira_fields_needed = ["status", "created", "summary", "project", "customfield_10002", "customfield_11115", "priority"] # customfield_10002 = Story Points
    all_jira_issues = jira_helper.get_jira_issues(search_query, jira_fields_needed, jira_url, jira_token, issue_history_needed=False)

    print('Data extracted from Jira...')
    output_folder_path = jira_helper.get_output_folder_path(exe_path)
    os.makedirs(name=output_folder_path, exist_ok=True)
    output_csv_file_fullpath = os.path.join(output_folder_path, output_file_name)
    csv_single_row_list = {
            "ID": 0,
            "summary": "", 
            #"jiralink": "",
            "status": "",
            "environment": "",
            "priority": "",
            "project key": "", 
            "project name": ""
            #"Story Point": ""
        }
    with open(output_csv_file_fullpath, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        header = csv_single_row_list.keys()
        csv_writer.writerow(header)
        for jira_issue in all_jira_issues:
            csv_single_row_list["ID"] =  jira_issue.key
            #csv_single_row_list["jiralink"] = f"{config[ConfigKeyConst.JIRA_URL_KEY.value]}/browse/{jira_issue.key}"
            csv_single_row_list["status"] = jira_issue.fields.status
            csv_single_row_list["project key"] = jira_issue.fields.project
            csv_single_row_list["project name"] = jira_issue.fields.project.name
            csv_single_row_list["priority"] = jira_issue.fields.priority.name
            if hasattr(jira_issue.fields, "customfield_11115") and  jira_issue.fields.customfield_11115 != None:
                csv_single_row_list["environment"] = jira_issue.get_field("customfield_11115")
            #csv_single_row_list[Story Point"] = jira_issue.get_field("customfield_10002")
            #csv_single_row_list["summary"] = jira_issue.fields.summary 
            # write to the object
            csv_writer.writerow(csv_single_row_list.values())
            csv_single_row_list =  dict.fromkeys(csv_single_row_list, None) # delete and clear all values
    print('\n')
    print(f"Issues fetched: {len(all_jira_issues)} records")
    print(f'CSV file {output_csv_file_fullpath} created...' + ' ' + str(datetime.now()))
except Exception as e:
    print(f"Error : {e}")
    print(e.__traceback__)  # Prints the traceback
