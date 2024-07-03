import csv
from datetime import datetime

import sys
import logging

from helper.credential.credential_manager import CredentialManager
from helper.utils.dateutil import DateUtil
from helper.jira_helper import JiraWorkItem
from helper.constants import JiraJsonKeyConstants as JiraJsonKeyConst, FileFolderNameConstants as FileFolderNameConst, ConfigKeyConstants as ConfigKeyConst, GeneralConstants as GeneralConst, DateUtilConstants as DateUtilConst 
import helper.jira_helper as jh
import helper.file_helper as fh
#import helper.flow_metrics_helper as fm_helper #UNCOMMENT ONLY WHEN DEPENDCY ISSUES ARE RESOLVED



def main(twig_format_mode=False):
    try:
        logging.basicConfig(filename=FileFolderNameConst.APP_LOG_FILENAME.value, filemode="w", level=logging.INFO )
        logger = logging.getLogger(__name__)
        script_path = fh.get_folder_path_for_file(__file__)
        app_config_file_full_path = fh.get_config_file_path(script_path, FileFolderNameConst.CONFIG_FILENAME.value)
        app_config = fh.read_config(app_config_file_full_path) # loading config file for this project
        jira_board_config_full_file_path = fh.get_config_file_path(script_path, app_config[ConfigKeyConst.JIRA_BOARD_CONFIG_FILENAME_KEY.value])
        jira_board_queries_config = fh.read_config(jira_board_config_full_file_path) # loading jira board configuratio  file for this project
        jira_url = app_config[ConfigKeyConst.JIRA_URL_KEY.value]
        active_boards = jh.get_all_active_jira_query_names(jira_board_queries_config)
        print('-----------------------------------------')
        print('List of Active Boards in the config are:')
        print('-----------------------------------------')
        for jira_board in active_boards:
            print(f"{active_boards.index(jira_board)}. {jira_board}")
        print('-----------------------------------------')
        input_index: int =  int(input('Type the number for the option (from the above list): '))
        obj_board = jh.get_jira_query_by_name(active_boards[input_index], jira_board_queries_config)
        if obj_board is None:
            print('!!! Invalid Query Name provided. Exiting code !!!')
            sys.exit()

        cred_manager = CredentialManager()
        jira_token = cred_manager.get_credential(app_config[ConfigKeyConst.JIRA_TOKEN_CONFIG_KEY.value])

        # check for board id, else use the columns from configuration file
        is_query_jira_board_enabled: bool = obj_board.get(JiraJsonKeyConst.QUERY_JIRA_BOARD.value)
        if is_query_jira_board_enabled != None and not obj_board[JiraJsonKeyConst.QUERY_JIRA_BOARD.value]:
            columns = obj_board[JiraJsonKeyConst.COLUMNS.value]
        else:
            cur_jira_board_config = jh.get_jira_board_config_by_id(int(obj_board[JiraJsonKeyConst.BOARD_ID.value]), jira_token, jira_url)
            filter_id = cur_jira_board_config[GeneralConst.FILTER_ID.value]
            if JiraJsonKeyConst.JQL_ISSUE_TYPE.value in obj_board and obj_board[JiraJsonKeyConst.JQL_ISSUE_TYPE.value] != "":
                obj_board[JiraJsonKeyConst.JQL.value] = f"filter = {filter_id} and {obj_board[JiraJsonKeyConst.JQL_ISSUE_TYPE.value]}" # concatinate the board filter with the config jql if mentioned
            columns = cur_jira_board_config[GeneralConst.BOARD_COLUMNS.value]
            print("---------------------------------------")
            print(f"Jira Board name: {cur_jira_board_config[GeneralConst.BOARD_NAME.value]}")
            print(f"Additional Query Filter applied: {obj_board[JiraJsonKeyConst.JQL_ISSUE_TYPE.value]}")
       
        # define a dictionary to specify the needed jira fields (apart form status change dates info ) which needs to be captured in the output
        # fields 
        #   - created & status = needed for the data and hence must always be here with value None
        dict_needed_jira_field_and_column_mapping: dict = {
            "created": None,
            "status": None,
        }
        if twig_format_mode:
            output_file_name = obj_board[JiraJsonKeyConst.NAME.value] + FileFolderNameConst.TWIG_OUTPUT_FILE_POSTFIX.value
            date_format = DateUtilConst.DATE_FORMAT_TWIG.value 
        else: # code for normal csv file other than the onbe specific for usage with Actionable Agile twig application
             #  Add/Update additional fields which are needed in the output csv
            dict_needed_jira_field_and_column_mapping.update({"status": "Status"})
            dict_needed_jira_field_and_column_mapping.update({"issuetype": "Issue Type"})
            #dict_needed_jira_field_and_column_mapping.update({"project": "Project Key"})
            #dict_needed_jira_field_and_column_mapping.update({"customfield_10002": "Story Point"})

            output_file_name = obj_board[JiraJsonKeyConst.NAME.value] + FileFolderNameConst.FM_OUTPUT_FILE_POSTFIX.value
            date_format = app_config[ConfigKeyConst.OUTPUT_DATE_FORMAT_KEY.value]

        date_utility = DateUtil(date_format=date_format)
        obj_jira_data = JiraWorkItem(search_query=obj_board[JiraJsonKeyConst.JQL.value], jira_board_columns=columns,
                                    output_file_name=output_file_name)

        print(f'Please wait, preparing data for "{obj_board[JiraJsonKeyConst.NAME.value]}"')
        
        additional_columns = list(dict_needed_jira_field_and_column_mapping.values()) 
        obj_jira_data.insert_additional_columns_to_csv(additional_columns)
        jira_fields_needed = list(dict_needed_jira_field_and_column_mapping.keys())
        all_jira_issues = jh.get_jira_issues(obj_jira_data.search_query, jira_fields_needed, jira_url, jira_token)

        print('Extracting status change information...')
        output_folder_path = fh.get_output_folder_path(script_path)
        output_csv_file_fullpath = fh.create_file_and_return_fullpath_with_name(output_folder_path, obj_jira_data.file_name)
        with open(output_csv_file_fullpath, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            header = obj_jira_data.csv_single_row_list.keys()
            csv_writer.writerow(header)
            for jira_issue in all_jira_issues:
                obj_jira_data.set_row_values_to_blank()
                # get first jira board column having mapped status - exclude columns with no mapped status on jira board like backlog in Kanban board sometime)
                first_column_having_mapped_status = obj_jira_data.get_first_column_having_mapped_status()
                # assign created date as the value for first column which has mapped status
                obj_jira_data.csv_single_row_list[first_column_having_mapped_status] = jira_issue.fields.created
                obj_jira_data.set_issue_id(jira_issue.key)
                mapped_column_final_issue_status = obj_jira_data.get_mapped_csvcolumn_for_status(
                    current_status=jira_issue.fields.status.name)
                for history in jira_issue.changelog.histories:
                    for item in history.items:
                        if item.field == "status" and item.toString != item.fromString :  # checking for status change in the history & that status did not change to same
                            mapped_column_current_issue_status = obj_jira_data.get_mapped_csvcolumn_for_status(
                                current_status=item.toString)
                            if mapped_column_current_issue_status == '' or mapped_column_current_issue_status is None:
                                logger.info(f'Status mapping missing for: {item.toString} | Issue ID: {obj_jira_data.csv_single_row_list[GeneralConst.ID_COLUMN_NAME.value]} | Change Date: {history.created}')
                                break

                            obj_jira_data.set_value_for_csvcolumn(mapped_csvcolumn_for_field=mapped_column_current_issue_status,
                                                        new_value=history.created)
                            obj_jira_data.clear_later_workflow_column_value(
                                mapped_column_for_status=mapped_column_current_issue_status)

                obj_jira_data.clear_later_workflow_column_value(mapped_column_final_issue_status)
                # set additional column values
                for field in dict_needed_jira_field_and_column_mapping:
                    if dict_needed_jira_field_and_column_mapping[field] != None and hasattr(jira_issue.fields, field):
                        field_value = getattr(jira_issue.fields, field)
                        obj_jira_data.set_value_for_csvcolumn(mapped_csvcolumn_for_field=dict_needed_jira_field_and_column_mapping[field],new_value=field_value)
                        #obj_jira_data.set_board_column_value("jiralink", f"{jira_url}/browse/{jira_issue.key}" ) # special case for issue URL in jira
                # add the change date (needed format) to the csv_row_list object and add to csv
                for column in obj_jira_data.jira_board_columns:
                    obj_jira_data.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]] = date_utility.convert_jira_date(
                        obj_jira_data.csv_single_row_list[column[JiraJsonKeyConst.COLUMN_NAME.value]])

                csv_writer.writerow(obj_jira_data.csv_single_row_list.values())
        print(f"{len(all_jira_issues)} records prepared.")
        print(f'Output File: {output_csv_file_fullpath}')
        print(f"Please check '{FileFolderNameConst.APP_LOG_FILENAME.value}' file for info on missing status mapping in the record, if any.")

        # ------------ Generate flow metric report if true -----------
        if(app_config.get(ConfigKeyConst.GENERATE_FLOW_METRICS_REPORT_KEY.value)):
            start_column_name =  columns[1][JiraJsonKeyConst.COLUMN_NAME.value]
            done_column_name = columns[len(columns)-1][JiraJsonKeyConst.COLUMN_NAME.value]
            #fm_helper.generate_flow_metrics_report(obj_board[JiraJsonKeyConst.NAME.value], output_csv_file_fullpath, start_column_name, done_column_name,GeneralConst.ID_COLUMN_NAME.value, date_format)
        # -------------
    except Exception as e:
        print(f"Error : {e}")

if __name__ == "__main__":   
    main()