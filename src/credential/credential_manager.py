import os


class CredentialManager:

    @staticmethod
    def get_credential(secret_name):
        return os.environ.get(secret_name)