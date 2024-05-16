

# Jira Flow Metrics Extractor  
This code extracts the Flow metrics for jira work items associated with a specific jira board  

## Initial Setup
1. Install python on your machine - python 3.11
   - Only for Windows
     - Set python path in the environment variable
3. Install Jira package - jira==3.8.0
   - Mac
     -Open terminal and install jira package
     - pip3 install jira
   - Windows
     -Open command line and install jira package
     - pip install jira
4. Create your Personal Jira Access Token which will be used by the program
   - https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
5. Creating and setting Environment variable for jira access token to save your Personal Jira Access Token
   - Mac Users
     - **Permanent Environment Variable:** This method makes the variable available across all terminal sessions, including new ones you open later.

        - **Identify your shell:**
            - Run the following command in your terminal to see which shell you're using (most likely `bash` or `zsh`):
                - `echo $SHELL`
        - **Edit your shell profile:** The specific profile file depends on your shell:
            - .**Zsh (default on macOS Big Sur or later):** Edit the `.zshrc` file in your home directory.Use a text editor like `nano` or `vim` to edit the file. You can open the file in your terminal with:
                - `nano ~/.zshrc # For zsh`
        - **Add the environment variable:** Inside the profile file, add a new line in the format:
            - `export jira_token=VALUE`
            
              - Replace `VALUE` with your personal jira access token.
        - **Save and source the file:** In your text editor, save the changes.In your terminal window, run the following command to reload the profile and make the variable available in the current session:
            - `source ~/.zshrc # For zsh`
            - `source ~/.bash_profile # For bash`
        - **Verifying the Environment Variable:**
            - To check if the environment variable is set correctly, run the following command in your terminal:
                - `echo $jira_token`
   - Windows Users
     - To create or modify environment variables on Windows:
        - Right-click the Computer icon and choose Properties, or in Windows Control Panel, choose System.
        - Choose Advanced system settings.
        - On the Advanced tab, click Environment Variables.
        - Click New to create a new environment variable.
          - variable name = `jira_token`
          - value = `your personal jira access token`


      - Reference link for help: https://docs.oracle.com/cd/E83411_01/OREAD/creating-and-modifying-environment-variables-on-windows.htm#OREAD158

## Configurations
1. Configuration Setting for this project

    File : `config/config.json`
    ```

    {
        "jira_url": "https://jira.abc.com",
        "jira_token_env_varname": "jira_token",
        "output_date_format": "yyyymmdd"
    }
    ```

    - `jira_url` => the url of your jira instance

    - `jira_token_env_varname` => for this code to execute, it requires your personal Jira token configured and set in the environment variable. The 'jira_token_env_varname' config setting should have the name of the name of the environment variable in which your personal Jira token resides.

    - `output_date_format` => This code supports 2 different date format as output
        - `"yyyymmdd"`       for TWiG - https://analytics.actionableagile.com/twig/index.html
        - `"dd.mm.yyyy"`     for normal excel operations

2. Configuration of the jira projects/board which needs to be executed

    File: `config/projectQueriesConfig.json`
      ```
        {
          "boards": [
            {
              "name": "PRAU Standard",
              "jql": "project= PRAU and issuetype in standardIssueTypes() and issuetype != Epic",
              "board_id": 12819
            },
            {
              "name": "Jira Admin",
              "jql": "project = 'JIRA Administration' AND issuetype not in (Epic, Program, subTaskIssueTypes())",
              "board_id": 3
            }
          ]
        }
      ```

   - `name` => Short name for the board configured. This will appear when you execute code as one of the options

   - `jql` => the jira JQL which needs to be run for fetching the data.
        - You can use the JQL for the jira board you wnat to configure but ensure that you modify the query to exclude the issue type which are needed for cycle time.
        - Please ensure that the JQL does not contain double quotes (") and are replaced by single quotes (')
   
   - `board_id` => the jira board id, for example (https://jira.abc.com/secure/RapidBoard.jspa?rapidView=12345) the number after rapidview
   
   - `active` => this is an optional value and can be set to `false` or `true`. This value ensures (non)visibility of this listing when the program is executed.


## Execution
- Execute the mainTWUGDataExtract.py and follow the instructions
