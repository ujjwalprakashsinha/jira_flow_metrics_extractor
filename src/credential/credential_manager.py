import os

class CredentialManager:
    #def __init__(self):
       
        # self.credentials = {
        #     "jira_token": jira_token,
        # }

    def get_credential(self, secret_name):
        return os.environ.get(secret_name)
        #return self.credentials[secret_name]

