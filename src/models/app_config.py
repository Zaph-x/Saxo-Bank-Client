from models.json_model_base import JsonModelBase


class AppConfig(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "AppName": {"type": "string", "minLength": 1},
            "AppKey": {"type": "string", "minLength": 1},
            "AuthorizationEndpoint": {"type": "string", "minLength": 1},
            "TokenEndpoint": {"type": "string", "minLength": 1},
            "GrantType": {"type": "string", "minLength": 1},
            "OpenApiBaseUrl": {"type": "string", "minLength": 1},
            "RedirectUrls": {"type": "array", "items": {"type": "string"}, "minItems": 1},
            "AppSecret": {"type": "string", "minLength": 1},
        },
        "required": [
            "AppName",
            "AppKey",
            "AuthorizationEndpoint",
            "TokenEndpoint",
            "GrantType",
            "OpenApiBaseUrl",
            "RedirectUrls",
            "AppSecret",
        ],
    }

    def __init__(
        self,
        app_name: str,
        app_key: str,
        app_secret: str,
        authorization_endpoint: str,
        token_endpoint: str,
        grant_type: str,
        open_api_base_url: str,
        redirect_urls: list[str],
    ):
        self.app_name = app_name
        self.app_key = app_key
        self.app_secret = app_secret
        self.authorization_endpoint = authorization_endpoint
        self.token_endpoint = token_endpoint
        self.grant_type = grant_type
        self.open_api_base_url = open_api_base_url
        self.redirect_urls = redirect_urls
