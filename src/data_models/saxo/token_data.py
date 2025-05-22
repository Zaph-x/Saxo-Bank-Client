from data_models.json_model_base import JsonModelBase


class TokenDataModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "access_token": {"type": "string", "minLength": 1},
            "expires_in": {"type": "number"},
            "refresh_token": {"type": "string", "minLength": 1},
            "token_type": {"type": "string", "minLength": 1},
            "refresh_token_expires_in": {"type": "number"},
            "base_uri": {"type": ["string", "null"], "minLength": 1},
        },
        "required": [
            "access_token",
            "expires_in",
            "refresh_token",
            "token_type",
            "refresh_token_expires_in",
        ],
    }

    def __init__(self, access_token, expires_in, refresh_token, token_type, refresh_token_expires_in, base_uri):
        self.access_token = access_token
        self.expires_in = expires_in
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.refresh_token_expires_in = refresh_token_expires_in
        self.base_uri = base_uri

    def is_expired(self):
        pass

    def __str__(self):
        return f"TokenDataModel(access_token={self.access_token[:5]}..., expires_in={self.expires_in}, refresh_token={self.refresh_token[:5]}..., token_type={self.token_type}, refresh_token_expires_in={self.refresh_token_expires_in}, base_uri={self.base_uri})"
