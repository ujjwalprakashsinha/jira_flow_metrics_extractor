from enum import Enum

class GeneralConstants(Enum):
    BOARD_COLUMNS = "board_columns"
    FILTER_ID = "filter_id"
    BOARD_NAME = "board_name"
    ID_COLUMN_NAME = "ID"

class JiraJsonKeyConstants(Enum):
    BOARDS = "boards"
    QUERY_JIRA_BOARD = "query_jira_board"
    NAME = "name"
    JQL_EXCLUDE_ISSUE_TYPE = "jql_exclude_issue_type"
    JQL = "jql"

    # where the specified option should be displayed or not
    SHOW = "show"

    # config key for jira board id fom which columns and statuses info will be retrieved.   
    BOARD_ID = "board_id"
    
    # config keys for situtaions when board id is not provide and henc columns and related statuses info are provided
    COLUMNS = "columns"
    COLUMN_NAME = "column_name"
    STATUSES = "statuses"


class DateUtilConstants(Enum):
    DATE_FORMAT_JIRA = "%Y-%m-%dT%H:%M:%S.%f%z"
    DATE_FORMAT_TWIG = "%Y%m%d"
    DATE_FORMAT_EXCEL = "%d.%m.%Y"


class FileFolderNameConstants(Enum):
    CONFIG_FILENAME = "config.yaml"
    OUTPUT_FOLDERNAME = "outputFiles"
    TWIG_OUTPUT_FILE_POSTFIX = "_fm_jira_data_twig.csv"
    FM_OUTPUT_FILE_POSTFIX = "_fm_jira_data.csv"
    ADF_OUTPUT_FILE_POSTFIX = "_adf_jira_data.csv"
    CONFIG_FOLDERNAME = "config"
    APP_LOG_FILENAME = "app.log"


class ConfigKeyConstants(Enum):
    JIRA_URL_KEY = "jira_url"
    JIRA_TOKEN_VARNAME_KEY = "jira_token_env_varname"
    OUTPUT_DATE_FORMAT_KEY = "output_date_format"
    JIRA_BOARD_CONFIG_FILENAME_KEY = "jira_board_config_filename"
    GENERATE_FLOW_METRICS_REPORT_KEY =  "generate_flow_metrics_report"
    JIRA_TOKEN_CONFIG_KEY = "jira_token_config"
    JIRA_TOKEN_CONFIG_MODE_KEY = "mode"
    JIRA_TOKEN_CONFIG_VALUE_KEY = "value"
    JIRA_TOKEN_CONFIG_MODE_ENV_VAR = "env_var"
    JIRA_TOKEN_CONFIG_MODE_STRING = "string"
