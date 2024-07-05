import os
from helper.constants import FileFolderNameConstants as FileFolderNameConst
import yaml

def _check_if_file_exists(file_path_with_name, raise_if_not_found = False):
    if not os.path.isfile(file_path_with_name):
        if raise_if_not_found:
            raise FileNotFoundError(f"The file '{file_path_with_name}' does not exist.")
        
        return False
    
    return True


def get_config_file_path(script_folder_path, file_name) -> str:
    return str(os.path.join(os.path.dirname(script_folder_path), FileFolderNameConst.CONFIG_FOLDERNAME.value, file_name))


def get_output_folder_path(script_path) -> str:
    return str(os.path.join(os.path.dirname(script_path), FileFolderNameConst.OUTPUT_FOLDERNAME.value))


def get_file_fullpath_with_name(folder_path, file_name) -> str:
    output_file_fullpath = os.path.join(folder_path, file_name) 
    return output_file_fullpath

def create_file_and_return_fullpath_with_name(folder_path, file_name) -> str:
    os.makedirs(name=folder_path, exist_ok=True)
    output_file_fullpath = os.path.join(folder_path, file_name)
    return output_file_fullpath


def get_folder_path_for_file(file_path_with_name: str) -> str:
    return os.path.dirname(file_path_with_name)


def read_config(file_path):
    print("Reading Config File from {0}".format(file_path))
    
    _check_if_file_exists(file_path, True)
    
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return config_data