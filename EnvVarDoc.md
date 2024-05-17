# How to create and modify environment variable 
Creating and setting Environment variable for jira access token to save your Personal Jira Access Token
- Mac Users
    - **Permanent Environment Variable:** This method makes the variable available across all terminal sessions, including new ones you open later.

        - **Identify your shell:**
            - Run the following command in your terminal to see which shell you're using (most likely `bash` or `zsh`):
                - `echo $SHELL`
        - **Edit your shell profile:** The specific profile file depends on your shell:
            - .**Zsh (default on macOS Big Sur or later):** Edit the `.zshrc` file in your home directory.Use a text editor like `nano` or `vim` to edit the file. You can open the file in your terminal with:
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
    - Right-click the Computer icon and choose Properties, or in Windows Control Panel, choose System.
    - Choose Advanced system settings.
    - On the Advanced tab, click Environment Variables.
    - Click New to create a new environment variable.
        - variable name = `jira_token`
        - value = `your personal jira access token`

    - Reference link for help: [Create/Modify Environment Variable on Windows machine](https://docs.oracle.com/cd/E83411_01/OREAD/creating-and-modifying-environment-variables-on-windows.htm#OREAD158)