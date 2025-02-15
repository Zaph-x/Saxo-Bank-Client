from models.json_model_base import JsonModelBase


class TokenDataModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "access_token": {"type": "string", "minLength": 1},
            "expires_in": {"type": "number"},
            "refresh_token": {"type": "string", "minLength": 1},
        },
        "required": [
            "access_token",
            "expires_in",
            "refresh_token",
        ],
    }

    def __init__(self, token, expires_in, refresh_token):
        self.access_token = token
        self.expires_in = expires_in
        self.refresh_token = refresh_token

    def __str__(self):
        return f"TokenDataModel(access_token={self.access_token[:5]}..., expires_in={self.expires_in}, refresh_token={self.refresh_token[:5]}...)"
