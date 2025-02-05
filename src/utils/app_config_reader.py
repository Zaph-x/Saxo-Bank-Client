import json


def read_app_config(file_path: str = "saxoapp.json") -> dict:
    with open(file_path) as f:
        config = json.load(f)
    return config
