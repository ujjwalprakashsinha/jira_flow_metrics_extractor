from enum import Enum

class GeneralConstants(Enum):
    BOARD_COLUMNS = "board_columns"
    FILTER_ID = "filter_id"
    BOARD_NAME = "board_name"

class JiraJsonKeyConstants(Enum):
    BOARDS = "boards"
    QUERY_JIRA_BOARD = "query_jira_board"
    NAME = "name"
    JQL_EXCLUDE = "jql_exclude"
    JQL = "jql"

    # where the specified option should be displayed or not
    ACTIVE = "active"

    # config key for jira board id fom which columns and statuses info will be retrieved.   
    BOARD_ID = "board_id"
    
    # config keys for situtaions when board id is not provide and henc columns and related statuses info are provided
    COLUMNS = "columns"
    COLUMN_NAME = "column_name"
    STATUSES = "statuses"


class DateUtilConstants(Enum):
    DATE_FORMAT_TWIG = "yyyymmdd"
    DATE_FORMAT_STANDARD = "dd.mm.yyyy"


class FileFolderNameConstants(Enum):
    CONFIG_FILENAME = "config.json"
    OUTPUT_FOLDERNAME = "outputFiles"
    TWIG_OUTPUT_FILE_POSTFIX = "_twig_jira_data.csv"
    COLUMN_OUTPUT_FILE_POSTFIX = "_column_jira_data.csv"
    CONFIG_FOLDERNAME = "config"


class ConfigKeyConstants(Enum):
    JIRA_URL_KEY = "jira_url"
    JIRA_TOKEN_VARNAME_KEY = "jira_token_env_varname"
    OUTPUT_DATE_FORMAT_KEY = "output_date_format"
    JIRA_BOARD_CONFIG_FILENAME = "jira_board_config_filename"
