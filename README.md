# jira_cycletime_code

Configurations:
1. Configuration Setting for this project

    File : config/config.json

    {
        "jira_url": "https://jira.sixt.com",
        "jira_token_env_varname": "jira_token",
        "output_date_format": "yyyymmdd"
    }

    - jira_url => the url of your jira instance

    - jira_token_env_varname => for this code to execute, it requires your personal Jira token configured and set in the environment variable. The 'jira_token_env_varname' config setting should have the name of the name of the environment variable in which your personal Jira token resides.

    - output_date_format => This code supports 2 different date format as output
        "yyyymmdd"      # for Twig
        "dd.mm.yyyy"    # for normal excel operations

2. Configuration of the jira projects/board which needs to be executed

    File: config/projectQueriesConfig.json

   {
    "queries": [
      {
        "name": "PRAU Standard",
        "query_text": "project= PRAU and issuetype in standardIssueTypes() and issuetype != Epic",
        "board_id": 12819
      },
      {
        "name": "Jira Admin",
        "query_text": "project = 'JIRA Administration' AND issuetype not in (Epic, Program, subTaskIssueTypes())",
        "board_id": 3
      }
    ]
   }

   - name => Short name for the board configured. This will appear when you execute code as one of the options

   - query_text => the jira JQL which needs to be run for fetching the data.
        - - You can use the JQL for the jira board you wnat to configure but ensure that you modify the query to exclude the issue type which are needed for cycle time.
        - -  Please ensure that the JQL does not contain double quotes (") and are replaced by single quotes (')
   
   - board_id => the jira board id, for example (https://jira.sixt.com/secure/RapidBoard.jspa?rapidView=12549) the number after rapidview