import os
from helper.constants import FileFolderNameConstants as FileFolderNameConst
import yaml

def get_config_file_path(exe_folder_path, file_name) -> str:
    return str(os.path.join(os.path.dirname(exe_folder_path), FileFolderNameConst.CONFIG_FOLDERNAME.value, file_name))


def get_output_folder_path(exe_folder) -> str:
    return str(os.path.join(os.path.dirname(exe_folder), FileFolderNameConst.OUTPUT_FOLDERNAME.value))


def check_if_file_exists(file_path, raise_if_not_found = False):
    if not os.path.isfile(file_path):
        if raise_if_not_found:
            raise FileNotFoundError(f"The file '{file_path}' does not exist.")
        
        return False
    
    return True


def read_config(file_path):
    print("Reading Config File from {0}".format(file_path))
    
    check_if_file_exists(file_path, True)
    
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data