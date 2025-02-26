import time
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


def ensure_yaml_exists(yaml_file):
    """Ensures the YAML file exists. Creates an empty one if not present."""
    os.makedirs(os.path.dirname(yaml_file), exist_ok=True)
    if not os.path.exists(yaml_file):
        with open(yaml_file, "w") as file:
            file.write("")  # Create an empty YAML file


# Load the YAML file
# def load_user_paths(yaml_file):
#     with open(yaml_file, 'r') as file:
#         data = yaml.safe_load(file)

#     if data is not None:
#         return NestedNamespace(**data)


def load_user_paths(yaml_file):
    """Loads the YAML file into a NestedNamespace object."""
    ensure_yaml_exists(yaml_file)  # Ensure the file exists before loading

    with open(yaml_file, "r") as file:
        data = yaml.safe_load(file) or {}  # Handle empty files gracefully

    return NestedNamespace(**data)


def load_store_configs():
    # LOAD YAML STORE CONFIGS, set as module attributes
    # Dynamically set attributes on the geogridfusion module for top-level keys
    yaml_file_path = os.path.join(
        os.path.dirname(__file__), "user_paths", "user_paths.yaml"
    )
    user_paths_data = load_user_paths(yaml_file_path)

    if user_paths_data is None:
        return

    # Dynamically set attributes on the geogridfusion module
    module = sys.modules["geogridfusion"]
    for key, value in user_paths_data.__dict__.items():
        setattr(module, key, value)


# move out of this
TREE_NAMES = ["tree_10km", "tree_4km"]


def empty_search_trees():
    module = sys.modules["geogridfusion"]

    for name in TREE_NAMES:
        setattr(module, name, None)
