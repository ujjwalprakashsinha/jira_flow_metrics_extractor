from enum import Enum

class JiraJsonKeyConstants(Enum):
    QUERIES = "queries"
    NAME = "name"
    QUERY_TEXT = "query_text"
    ACTIVE = "active"
    COLUMNS = "columns"
    COLUMN_NAME = "column_name"
    STATUSES = "statuses"
    
   

class DateUtilConstants(Enum):
    DATE_FORMAT_TWIG = "yyyymmdd"
    DATE_FORMAT_STANDARD = "dd.mm.yyyy" 

class FileFolderNameConstants(Enum):
    PROJECT_QUERY_CONFIG_FILENAME = "projectQueriesConfig.json"
    CONFIG_FILENAME = "config.json"
    OUTPUT_FOLDERNAME =  "outputFiles"
    OUTPUT_FILE_POSTFIX = "_raw_jira_data.csv"
    CONFIG_FOLDERNAME = "config"

class ConfigKeyConstants(Enum):
    JIRA_URL_KEY = "jira_url"
    JIRA_TOKEN_VARNAME_KEY = "jira_token_env_varname"
    OUTPUT_DATE_FORMAT_KEY = "output_date_format"
