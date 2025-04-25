from data_models.app_config import AppConfig


def read_app_config(file_path: str = "saxoapp.json") -> AppConfig:
    with open(file_path) as f:
        config = AppConfig.from_json(f.read())
    return config
