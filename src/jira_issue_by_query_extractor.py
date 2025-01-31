import csv
from datetime import datetime
import pandas as pd

from helper.credential.credential_manager import CredentialManager
from helper.constants import FileFolderNameConstants as FileFolderNameConst, ConfigKeyConstants as ConfigKeyConst
import helper.jira_helper as jh
import helper.file_helper as fh

# ***** The Main code execution starts here ****
def main():
    try:
        script_path = fh.get_folder_path_for_file(__file__) #os.path.dirname(__file__)
        app_config_file_full_path = fh.get_config_file_path(script_path, FileFolderNameConst.CONFIG_FILENAME.value)
        app_config = fh.read_config(app_config_file_full_path) # loading config file for this project
        jira_url = app_config[ConfigKeyConst.JIRA_URL_KEY.value]
        
        cred_manager = CredentialManager()
        jira_token = cred_manager.get_credential(app_config[ConfigKeyConst.JIRA_TOKEN_CONFIG_KEY.value])
        
        
        # search_query = "issuetype = Bug and statusCategory in ('To Do', 'In Progress')" # the search query
        search_query = "resolution is EMPTY and statusCategory = Done"
        #search_query = "project=AD and statusCategory = 'To Do'"
        # search_query = "filter = 27620 AND resolutiondate >= -300d AND resolutiondate >= 2024-06-02 AND resolutiondate < 2024-06-09" # the search query

        mapping = {"created": None, "status": None}
        fields = {
            "project": "Project",             
            "priority": "Priority",
            "status": "Status",
            "resolution": "Resolution",
            "issuetype": "Type",
            "customfield_10005": "Epic Link", 
            "customfield_11115": "Environment",
            "updated": "Updated Date"
            # "labels": "Labels", 
            # customfield_10002: "Story Points"
            # "components": "Components"
        }
        mapping.update(fields)
        all_jira_issues = jh.get_jira_issues(search_query, list(mapping.keys()), jira_url, jira_token, issue_history_needed=False)

        #####
        
        additional_field_dataset = []
        for jira_issue in all_jira_issues:
            jira_issue_with_field_data = jh.capture_additional_field_value(jira_issue=jira_issue, field_and_column_mapping=mapping)
            additional_field_dataset.append(jira_issue_with_field_data.copy())            
        #####

        print('Data extracted from Jira...')
        output_file_name = "Jira_Query_Export_Data.xlsx" 
        output_folder_path = fh.get_output_folder_path(script_path)
        output_csv_file_fullpath = fh.create_file_and_return_fullpath_with_name(output_folder_path, output_file_name)

        flow_metric_dataframe = pd.DataFrame(additional_field_dataset)
        flow_metric_dataframe.to_excel(output_csv_file_fullpath, index=False)
        print(f"{len(all_jira_issues)} records prepared.")
        print(f'Output Files: \n \t{output_csv_file_fullpath} \n')
    except Exception as e:
        print(f"Error : {e}")
        print(e.__traceback__)  # Prints the traceback

if __name__ == "__main__":   
    main()
