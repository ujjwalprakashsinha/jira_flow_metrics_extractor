import os


class CredentialManager:

    @staticmethod
    def get_credential(secret_name):
        credential_value = os.environ.get(secret_name)
        if not credential_value:
            raise Exception(f"The provided credential {secret_name} is either empty or does not exists")
        return credential_value