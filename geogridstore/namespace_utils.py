import yaml
import sys
import os

class NestedNamespace:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if isinstance(value, dict):
                # Recursively convert nested dictionaries to NestedNamespace
                setattr(self, key, NestedNamespace(**value))
            else:
                setattr(self, key, value)
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"

# Load the YAML file
def load_user_paths(yaml_file):
    with open(yaml_file, 'r') as file:
        data = yaml.safe_load(file)

    if data is not None:
        return NestedNamespace(**data)

def load_store_configs():
    # LOAD YAML STORE CONFIGS, set as module attributes
    # Dynamically set attributes on the geogridstore module for top-level keys
    yaml_file_path = os.path.join(os.path.dirname(__file__), "user_paths", "user_paths.yaml")
    user_paths_data = load_user_paths(yaml_file_path)

    if user_paths_data is None:
        return

    # Dynamically set attributes on the geogridstore module
    module = sys.modules['geogridstore']
    for key, value in user_paths_data.__dict__.items():
        setattr(module, key, value)
