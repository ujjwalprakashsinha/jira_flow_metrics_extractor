<div align="center" id="top"> 
  <img src="/resources/img/jfme.jpeg" alt="Jira Flow Metric Extractor Code" width="200" height="150" />

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
The extracted data can be used to generate insights which helps the team to effectively inspect and adapt.

**Below are the list of flow metrics**
- Cycle Time: time it takes to complete one unit of work from start to finish ( `End date - Start date + 1` )
- Workitem Issue Age: the amount of time a specific task (work item) has been in progress since it first started.
- Work In Progress Count: the total number of tasks or items that are currently being worked on but haven't yet been finished.
- Throughput:  the rate at which something gets completed.

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

-Before starting :checkered_flag:, you need to have following things
  - Installed the required packages.
    - Mac
      - Open terminal, go to the project directory and install package using requirement.txt (you will find the requirement.txt under the project folder)
        - `pip3 install -r requirement.txt`
    - Windows
      - Open command line, go to the project directory and install package using requirement.txt
        - `pip install -r requirement.txt`
  - Create your Personal Jira Access Token (for your/your companies jira instance) which will be used by the program
    - check this for reference on how to create personal token: [manage-api-tokens-for-your-atlassian-account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/){:target="_blank"} 
  - Creating and setting Environment variable for jira access token `jira_token` to save your Personal Jira Access Token. Check details [Setting Environment Variable](EnvVarDoc.md){:target="_blank"}
  
## :robot: Configurations ##
:pushpin: Please create 2 configuration files under `config` folder :file_folder: with below name and content. Update the config values to match your requirements.
:scissors: You can find sample config files under :file_folder: `config` folder which you can rename for quick start.

1. Configuration Setting for this project

    File : `config/config.yaml`
    ```
    # How to connect to JIRA?
    jira_url: https://jira.abc.com # the url of your jira instance
    jira_token_env_varname: jira_token
    # jira_token_env_varname: for this code to execute, it requires your personal Jira token configured and set in the environment variable. 
    # The 'jira_token_env_varname' config setting should have the name of the name of the environment variable in which your personal Jira token resides.

    # output date format
    output_date_format: "%Y%m%d" # all python supported date formates are including "%Y%m%d" (for TWiG) & "%d.%m.%Y" (standard excel) which will be used for the final output file
    #jira board configuration file name
    jira_board_config_filename: jira_board_config.yaml 
    ```

    - `jira_url` => the url of your jira instance

    - `jira_token_env_varname` => for this code to execute, it requires your personal Jira token configured and set in the environment variable. The 'jira_token_env_varname' config setting should have the name of the name of the environment variable in which your personal Jira token resides.

    - `output_date_format` => Check [Python Dates](https://www.w3schools.com/python/python_datetime.asp) for the options you have (or ask ChatGPT). Below are couple of examples
        - `"%Y%m%d"`       for [TWiG by ActionableAgile](https://analytics.actionableagile.com/twig/index.html){:target="_blank"}
        - `"%d.%m.%Y"`     for standard excel operations
    
    - `jira_board_config_filename` => name of the configuration file to get jira board setting. This file should reside under config folder

2. Configuration of the jira board from which the data will be extracted

    File: `config/jira_board_config.yaml`
      ```
        boards:
        - name: SAMPLE1
          query_jira_board: true
          jql_issue_type: "issuetype not in (Epic, Program, Test, subTaskIssueTypes())"
          board_id: 12819
        - name: Jira
          query_jira_board: true
          jql_issue_type: "issuetype not in (Epic, Program, Test, subTaskIssueTypes())"
          board_id: 11102
      ```

   - `name` => Short name for the board configured. This will appear when you execute code as one of the options

   - `query_jira_board` => value should be `true`. It specifies that the program will fetch jira query (jql) and board workflow from the specified board id.

   - `jql_issue_type` => part of jira JQL which defined the type of issues to select or exclude. If this attribute is not mentioned then all issue types from the board are retrieved. 
        - You can speific the jql with issuetype (exclude or include the issue type which are needed for cycle time).
        - Please ensure that the JQL does not contain double quotes (") and are replaced by single quotes (')
   
   - `board_id` => the jira board id, for example (https://jira.abc.com/secure/RapidBoard.jspa?rapidView=12345){:target="_blank"} the number after rapidview. This board info will be used for getting issues and related board workflow.
   
   - `show` => this is an optional value and can be set to `show: false` or `show: true`. This value ensures (non) visibility of this listing when the program is executed.

## :checkered_flag: Starting ##

```bash
# Clone this project or you can copy the repo on to your machine..
$ git clone https://github.com/ujjwalprakashsinha/jira_cycletime_code

# Access
$ cd jira_cycletime_code/src

# Install dependencies
$ pip3 install -r requirement.txt

# Run the project
$ python mainTWIGDataExtract.py

```

## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.


Made with :heart: by <a href="https://github.com/ujjwalprakashsinha" target="_blank">Ujjwal Sinha</a>

&#xa0;

<a href="#top">Back to top</a>
