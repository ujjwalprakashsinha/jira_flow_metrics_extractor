<div align="center" id="top"> 
  <img src="/resources/img/jfmr.jpeg" alt="Jira Flow Metric Extractor Code" />

  &#xa0;

</div>

<h1 align="center">Jira Flow Metric Extractor Code 🚀 </h1>


<h4 align="center"> 
	🚧  Under construction...  🚧
</h4> 

<hr> 

<p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-Configurations">Configurations</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/ujjwalprakashsinha" target="_blank">Author</a>
</p>

<br>

## :dart: About ##

This code extracts the Flow metrics for jira work items associated with a specific jira board - i.e how long issues spend in different stages of a workflow in Jira.
The extracted data can be used to generate insights which heps the team to effectively inspect and adapte.

**Below are the list of flow metrics**
- Cycle Time
- Workitem Issue Age
- Work In Progress Count
- Throughout

**What it does:**

- Connects to your Jira instance using your credentials.
- Allows you to choose a specific project query (board) to analyze.
- Figures out the different stages (columns) in that workflow.
- Retrieves all issues associated with the chosen query.
- Analyzes the issue history to see when each issue moved between stages.
- Saves the results to a CSV file for further analysis.

## :sparkles: Features ##

:heavy_check_mark: Understand how efficiently your team is working by identifying bottlenecks in the workflow;\
:heavy_check_mark: Track how issues are aging in your system;\
:heavy_check_mark: Super charge your planning and forecast based on real data;


## :white_check_mark: Requirements ##

-Before starting :checkered_flag:, you need to have jira package (jira==3.8.0) installed.
  - Mac
    -Open terminal and install jira package
    - pip3 install jira
  - Windows
    -Open command line and install jira package
    - pip install jira
- Create your Personal Jira Access Token (for your/your companies jira instance) which will be used by the program
   - check this for reference on how to create personal token: [manage-api-tokens-for-your-atlassian-account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) 
- Creating and setting Environment variable for jira access token `jira_token` to save your Personal Jira Access Token. Check details [Setting Environment Variable](EnvVarDoc.md)
  
## :robot: Configurations ##
:pushpin: Please create 2 configuration files under `config` folder :file_folder: with below name and content. Update the config values to match your requirements.
:scissors: You can find sample config files under :file_folder: `resources/sample` folder which you can copy under `config` folder for quick start.

1. Configuration Setting for this project

    File : `config/config.json`
    ```
    {
        "jira_url": "https://jira.abc.com",
        "jira_token_env_varname": "jira_token",
        "output_date_format": "yyyymmdd",
        "jira_board_config_filename": "jira_board_config.json"
    }
    ```

    - `jira_url` => the url of your jira instance

    - `jira_token_env_varname` => for this code to execute, it requires your personal Jira token configured and set in the environment variable. The 'jira_token_env_varname' config setting should have the name of the name of the environment variable in which your personal Jira token resides.

    - `output_date_format` => This code supports 2 different date format as output
        - `"yyyymmdd"`       for [TWiG by ActionableAgile](https://analytics.actionableagile.com/twig/index.html)
        - `"dd.mm.yyyy"`     for normal excel operations
    
    - `jira_board_config_filename` => name of the configuration file to get jira board setting. This file should reside under config folder

2. Configuration of the jira board from which the data will be extracted

    File: `config/jira_board_config.json`
      ```
        {
          "boards": [
            {
              "name": "JFLE",
              "jql": "project= JELE and issuetype in standardIssueTypes() and issuetype != Epic",
              "board_id": 1234
            },
            {
              "name": "Jira",
              "jql": "project = 'JIRA' AND issuetype not in (Epic, Program, subTaskIssueTypes())",
              "board_id": 5678
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
  
  > [!NOTE]
  > Please ensure that the last board setting in the configuration file does not have a comma (,) at the end.

## :checkered_flag: Starting ##

```bash
# Clone this project or you can copy the repo on to your machine..
$ git clone https://github.com/ujjwalprakashsinha/jira_cycletime_code

# Access
$ cd jira_cycletime_code/src

# Install dependencies
$ pip install jira

# Run the project
$ python mainTWIGDataExtract.py

```

## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/ujjwalprakashsinha" target="_blank">Ujjwal Sinha</a>

&#xa0;

<a href="#top">Back to top</a>
