import logging
import sys
import pandas as pd

from helper.credential.credential_manager import CredentialManager
from helper.jira_helper import JiraWorkItem
from helper.constants import JiraJsonKeyConstants as JiraJsonKeyConst, FileFolderNameConstants as FileFolderNameConst, ConfigKeyConstants as ConfigKeyConst, GeneralConstants as GeneralConst, DateUtilConstants as DateUtilConst 
import helper.jira_helper as jh
import helper.file_helper as fh
#import helper.flow_metrics_helper as fm_helper #UNCOMMENT ONLY WHEN DEPENDCY ISSUES ARE RESOLVED
from  helper.utils.dateutil import DateUtil



def setup_logging():
    logging.basicConfig(filename=FileFolderNameConst.APP_LOG_FILENAME.value, filemode="w", level=logging.INFO)
    return logging.getLogger(__name__)

def load_configurations(script_path):
    app_config_file_full_path = fh.get_config_file_path(script_path, FileFolderNameConst.CONFIG_FILENAME.value)
    app_config = fh.read_config(app_config_file_full_path)
    jira_board_config_full_file_path = fh.get_config_file_path(script_path, app_config[ConfigKeyConst.JIRA_BOARD_CONFIG_FILENAME_KEY.value])
    jira_board_queries_config = fh.read_config(jira_board_config_full_file_path)
    return app_config, jira_board_queries_config

def select_jira_board(jira_board_queries_config):
    active_boards = jh.get_all_active_jira_query_names(jira_board_queries_config)
    print('-----------------------------------------')
    print('List of Active Boards in the config are:')
    print('-----------------------------------------')
    for index, jira_board in enumerate(active_boards):
        print(f"{index}. {jira_board}")
    print('-----------------------------------------')
    input_index = int(input('Type the number for the option (from the above list): '))
    return jh.get_jira_query_by_name(active_boards[input_index], jira_board_queries_config)

def all_jira_boards(jira_board_queries_config):
    active_boards = jh.get_all_active_jira_query_names(jira_board_queries_config)
    print('-----------------------------------------')
    print('List of Active Boards in the config are:')
    print('-----------------------------------------')
    for index, jira_board in enumerate(active_boards):
        print(f"{index}. {jira_board}")
    print('-----------------------------------------')
    input_index = int(input('Type the number for the option (from the above list): '))
    return jh.get_jira_query_by_name(active_boards[input_index], jira_board_queries_config)

def get_jira_token(app_config):
    cred_manager = CredentialManager()
    return cred_manager.get_credential(app_config[ConfigKeyConst.JIRA_TOKEN_CONFIG_KEY.value])

def get_board_columns_and_jql(obj_board, jira_url, jira_token):
    is_query_jira_board_enabled = obj_board.get(JiraJsonKeyConst.QUERY_JIRA_BOARD.value)
    if is_query_jira_board_enabled is not None and not is_query_jira_board_enabled:
        columns = obj_board[JiraJsonKeyConst.COLUMNS.value]
    else:
        cur_jira_board_config = jh.get_jira_board_config_by_id(int(obj_board[JiraJsonKeyConst.BOARD_ID.value]), jira_url, jira_token )
        filter_id = cur_jira_board_config[GeneralConst.FILTER_ID.value]
        exclude_query = ""
        excluded_issue_types = obj_board.get(JiraJsonKeyConst.JQL_EXCLUDE_ISSUE_TYPE.value, "")
        if excluded_issue_types:
            exclude_query = f" and issuetype not in ({excluded_issue_types})"
        obj_board[JiraJsonKeyConst.JQL.value] = f"filter = {filter_id}{exclude_query}"
        columns = cur_jira_board_config[GeneralConst.BOARD_COLUMNS.value]
        print_board_info(cur_jira_board_config, excluded_issue_types)
    return columns

def print_board_info(cur_jira_board_config, excluded_issue_types):
    print("---------------------------------------")
    print(f"Jira Board name: \n \t{cur_jira_board_config[GeneralConst.BOARD_NAME.value]}")
    print(f"Excluded Issue Type/s: \n \t{excluded_issue_types}")

def prepare_output_file_paths(script_path, selected_board_name):
    output_folder_path = fh.get_output_folder_path(script_path)
    file_names = {
        "fm_output": selected_board_name + FileFolderNameConst.FM_OUTPUT_FILE_POSTFIX.value + FileFolderNameConst.CSV_FILE_EXTENSION.value,
        "adf_output": selected_board_name + FileFolderNameConst.ADF_OUTPUT_FILE_POSTFIX.value + FileFolderNameConst.CSV_FILE_EXTENSION.value,
        "merged_output": selected_board_name + FileFolderNameConst.MERGED_OUTPUT_FILE_POSTFIX.value + FileFolderNameConst.CSV_FILE_EXTENSION.value,
    }
    return {
        key: fh.create_file_and_return_fullpath_with_name(output_folder_path, file_name)
        for key, file_name in file_names.items()
    }

def add_additional_fields_to_query(mapping):
    fields = {
        "status": "Status", 
        "resolution": "Resolution",
        "issuetype": "Type",
        "labels": "Labels", 
        "customfield_10005": "Epic Link", 
        "customfield_11115": "Environment",
        "components": "Components"
    }
    mapping.update(fields)

def process_jira_issues(all_jira_issues, obj_jira_data, output_date_format, mapping):
    flow_metric_dataset = []
    additional_field_dataset = []
    for jira_issue in all_jira_issues:
        jira_issue_with_fm_data = jh.capture_issue_status_change_history(jira_issue=jira_issue, obj_jira_data=obj_jira_data, date_format=output_date_format)
        jira_issue_with_field_data = jh.capture_additional_field_value(jira_issue=jira_issue, field_and_column_mapping=mapping)
        additional_field_dataset.append(jira_issue_with_field_data.copy())
        flow_metric_dataset.append(jira_issue_with_fm_data.copy())
    return flow_metric_dataset, additional_field_dataset

def save_datasets(flow_metric_dataset, additional_field_dataset, file_paths, jira_url):
    flow_metric_dataframe = pd.DataFrame(flow_metric_dataset)
    flow_metric_dataframe.to_csv(file_paths["fm_output"], index=False)
    additional_field_dataframe = pd.DataFrame(additional_field_dataset)
    additional_field_dataframe['Link'] = jira_url + "/browse/" + additional_field_dataframe[GeneralConst.ID_COLUMN_NAME.value]
    additional_field_dataframe.to_csv(file_paths["adf_output"], index=False)
    merged_df = pd.merge(flow_metric_dataframe, additional_field_dataframe, on=GeneralConst.ID_COLUMN_NAME.value, how='inner')
    merged_df = process_merged_dataframe(merged_df)
    merged_df.to_csv(file_paths["merged_output"], index=False)

def process_merged_dataframe(merged_df):
    if "Labels" in merged_df.columns:
        merged_df = replace_commas_in_list_of_strings(merged_df, 'Labels')
        #merged_df['Labels'] = merged_df['Labels'].apply(lambda x: x.replace(',', '|'))
    if "Link" in merged_df.columns:
        cols = merged_df.columns.tolist()
        cols.remove('Link')
        cols.insert(1, 'Link')
        merged_df = merged_df[cols]
    return merged_df

def generate_date_file(flow_metric_dataframe, output_folder_path, selected_board_name, output_date_format):
    earliest_date = flow_metric_dataframe.iloc[:, 1].min()
    obj_date_util = DateUtil(output_date_format)
    all_dates_till_today = obj_date_util.get_all_date_till_today(earliest_date)
    all_dates_dataframe = pd.DataFrame(all_dates_till_today)
    date_output_csv_file_fullpath = fh.create_file_and_return_fullpath_with_name(output_folder_path, selected_board_name + "_dates.csv")
    all_dates_dataframe.to_csv(date_output_csv_file_fullpath, index=False)

# Function to replace commas with pipes in each string of the list
def replace_commas(lst):
    return [s.replace(',', '|') for s in lst]

# Function to join list items with a pipe delimiter
def join_with_pipe(lst):
    return '|'.join(lst)


def replace_commas_in_list_of_strings(df, column_name):
    # Define a helper function to replace commas with pipes in each string of a list
    def replace_commas(lst):
        return [s.replace(',', '|') for s in lst]
    
    # Apply the helper function to each list in the specified column
    df[column_name] = df[column_name].apply(replace_commas)
    return df


def main(output_date_format: str):
    try:
        logger = setup_logging()
        script_path = fh.get_folder_path_for_file(__file__)
        app_config, jira_board_queries_config = load_configurations(script_path)
        jira_token = get_jira_token(app_config)
        jira_url = app_config[ConfigKeyConst.JIRA_URL_KEY.value]
        obj_board = select_jira_board(jira_board_queries_config)
        
        if obj_board is None:
            print('!!! Invalid Query Name provided. Exiting code !!!')
            sys.exit()

        
        columns = get_board_columns_and_jql(obj_board, jira_url, jira_token)

        if not output_date_format:
            output_date_format = app_config[ConfigKeyConst.OUTPUT_DATE_FORMAT_KEY.value]

        print(f"Output Date format: \n \t{output_date_format}")
        selected_board_name = obj_board[JiraJsonKeyConst.NAME.value]
        file_paths = prepare_output_file_paths(script_path, selected_board_name)
        
        dict_needed_jira_field_and_column_mapping = {"created": None, "status": None}
        add_additional_fields_to_query(dict_needed_jira_field_and_column_mapping)
        
        obj_jira_data = JiraWorkItem(search_query=obj_board[JiraJsonKeyConst.JQL.value], jira_board_columns=columns, output_file_name=file_paths["fm_output"])
        print(f'Please wait, preparing data for "{selected_board_name}"')
        
        jira_fields_needed = list(dict_needed_jira_field_and_column_mapping.keys())
        all_jira_issues = jh.get_jira_issues(obj_jira_data.search_query, jira_fields_needed, jira_url, jira_token)

        print('Extracting status change information...')
        
        flow_metric_dataset, additional_field_dataset = process_jira_issues(all_jira_issues, obj_jira_data, output_date_format, dict_needed_jira_field_and_column_mapping)
        save_datasets(flow_metric_dataset, additional_field_dataset, file_paths, jira_url)
        generate_date_file(pd.DataFrame(flow_metric_dataset), fh.get_output_folder_path(script_path), selected_board_name, output_date_format)

        print(f"{len(all_jira_issues)} records prepared.")
        print(f'Output Files: \n \t{file_paths["merged_output"]} \n \t{file_paths["fm_output"]} \n \t{file_paths["adf_output"]}')
        print(f"Please check '{FileFolderNameConst.APP_LOG_FILENAME.value}' file for info on missing status mapping in the record, if any.")

    except Exception as e:
        print(f"Error : {e}")
        logger.error(f"Error : {e}")


if __name__ == "__main__": 
    main(output_date_format="")