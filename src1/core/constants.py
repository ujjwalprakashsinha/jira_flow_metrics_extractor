from enum import Enum

class ConfigKeyConstants(Enum):
    JIRA_URL = "jira_url"
    JIRA_TOKEN = "jira_token"
    JQL_QUERY = "jql_query"
    OUTPUT_PATH = "output_path"
    DATE_FORMAT = "date_format"
    JIRA_URL_KEY = "jira_url"
    JIRA_TOKEN_VARNAME_KEY = "jira_token_env_varname"
    OUTPUT_DATE_FORMAT_KEY = "output_date_format"
    JIRA_BOARD_CONFIG_FILENAME_KEY = "jira_board_config_filename"
    GENERATE_FLOW_METRICS_REPORT_KEY = "generate_flow_metrics_report"
    JIRA_TOKEN_CONFIG_KEY = "jira_token_config"
    JIRA_TOKEN_CONFIG_MODE_KEY = "mode"
    JIRA_TOKEN_CONFIG_VALUE_KEY = "value"
    JIRA_TOKEN_CONFIG_MODE_ENV_VAR = "env_var"
    JIRA_TOKEN_CONFIG_MODE_STRING = "string"

class JiraFieldConstants(Enum):
    STATUS = "status"
    CREATED = "created"
    UPDATED = "updated"
    RESOLUTION_DATE = "resolutiondate"
    ISSUE_TYPE = "issuetype"
    PRIORITY = "priority"

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
    SHOW = "show"
    BOARD_ID = "board_id"
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
    FM_OUTPUT_FILE_POSTFIX = "_fm_jira_data"
    ADF_OUTPUT_FILE_POSTFIX = "_adf"
    MERGED_OUTPUT_FILE_POSTFIX = "_merged"
    CONFIG_FOLDERNAME = "configs"
    APP_LOG_FILENAME = "app.log"
    CSV_FILE_EXTENSION = ".csv"

# Default values
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_FIELDS = ["key", "summary", "status", "created", "updated"] 