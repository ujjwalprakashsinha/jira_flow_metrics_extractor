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
  - **Install the required packages**
    - Mac
      - Open terminal, go to the project directory and install package using requirement.txt (you will find the requirement.txt under the project folder)
        - `pip3 install -r requirement.txt`
    - Windows
      - Open command line, go to the project directory and install package using requirement.txt
        - `pip install -r requirement.txt`
  - **Create Personal Jira Access Token**: create your personal jira access token (from your jira instance)
    - check this for reference on how to create personal token: [manage-api-tokens-for-your-atlassian-account](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)  
  - **Store Jira Token**: you can either store the jira token in your machine's environment variable or as plain text in this code's configuration file.
    - **Store in Environment Variable**: Set an environment variable on your machine to store your jira token value. Please remember the name of the environment variable (for example: `jira_token`) which will be used in the application configuration settings. Check details -> [Setting Environment Variable](EnvVarDoc.md) 
    - **Storing in application configuration file**: details provided in the configuration section.
  
## :robot: Configurations ##
:pushpin: Please create 2 configuration files under `config` folder :file_folder: with below name and content. Update the config values to match your requirements.
:scissors: You can find sample config files under :file_folder: `config` folder which you can rename for quick start.

1. Configuration Setting for this project

    File : `config/config.yaml`
    ```
   # How to connect to JIRA?
    jira_url: https://jira.abc.com # the url of your jira instance

    jira_token_config: 
      mode: env_var # env_var or string
      value: jira_token # if (mode = env_var) then environment variable name. if (mode = string) then personal jira token value.

    # output date format
    output_date_format: "%d/%m/%Y" # all python supported date format
    #jira board configuration file name
    jira_board_config_filename: jira_board_config.yaml 
    generate_flow_metrics_report: false # true or false based on if the flow metrics reports need to be generated
    ```

    | Name  | Description | Default Value |
    | :----| :----      | :---         |
    | `jira_url`| the url of your jira instance| None |
    | `jira_token_config`| Jira token related configuration settings| None |
    | `mode`| Specifies the mode for stoarge for the jira token. It can either be set to `env_var` if the token is saved in your machine's environment variable or `string` if you want to store it in this configuration file. | None |
    | `value`| It should either specify the environment variable name if `mode: env_var` or the value of your jira token if `mode: string` | None |
    | `output_date_format`| Check [Python Dates](https://www.w3schools.com/python/python_datetime.asp) for the options you have (or ask ChatGPT). For example <br> * `"%Y%m%d"` for [TWiG by ActionableAgile](https://analytics.actionableagile.com/twig/index.html) <br> * `"%d.%m.%Y"` for standard excel operations | None |
    | `jira_board_config_filename`| Name of the configuration file to get jira board related setting. This file should reside under config folder| None |
    | `generate_flow_metrics_report`| This feature of generating Flow Graphs is still under construction, so either omit/remove this or set it to `false`. | false |

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

    | Name  | Description | Default Value |
    | :----| :----      | :---         |
    |`name`|Short name for the board configured. This will appear when you execute code as one of the options|None|
    |`query_jira_board`|value should be `true`. It specifies that the program will fetch jira query (jql) and board workflow from the specified board id.|None|
    |`jql_issue_type`| Specify the part of jira JQL which defined the type of issues to select or exclude. If this attribute is not mentioned then all issue types from the board are retrieved. <br> * You can speific the jql with issuetype (exclude or include the issue type which are needed for cycle time). <br> * Please ensure that the JQL does not contain double quotes (") and are replaced by single quotes (')|None|
    |`board_id`|the jira board id, for example (https://jira.abc.com/secure/RapidBoard.jspa?rapidView=12345)  the number after rapidview. This board info will be used for getting issues and related board workflow.|None|
    |`show`|this is an optional value and can be set to `show: false` or `show: true`. This value ensures (non) visibility of this listing when the program is executed.|true|

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
