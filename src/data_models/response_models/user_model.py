from data_models.json_model_base import JsonModelBase


class UserModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "AssociatedAccountGroupOperations": {"type": "array"},
            "AssociatedAccountOperations": {"type": "array"},
            "AssociatedClientOperations": {"type": "array"},
            "AssociatedUserOperations": {"type": "array"},
            "ClientId": {"type": "number"},
            "ElevatedOperations": {"type": "array"},
            "GeneralOperations": {"type": "array"},
            "LinkedOperations": {"type": "array"},
            "UserId": {"type": "number"},
        },
        "required": [
            "AssociatedAccountGroupOperations",
            "AssociatedAccountOperations",
            "AssociatedClientOperations",
            "AssociatedUserOperations",
            "ClientId",
            "ElevatedOperations",
            "GeneralOperations",
            "LinkedOperations",
            "UserId",
        ],
    }

    def __init__(
        self: "UserModel",
        associated_account_group_operations: list,
        associated_account_operations: list,
        associated_client_operations: list,
        associated_user_operations: list,
        client_id: int,
        elevated_operations: list,
        general_operations: list,
        linked_operations: list,
        user_id: int,
    ) -> None:
        self.associated_account_group_operations = associated_account_group_operations
        self.associated_account_operations = associated_account_operations
        self.associated_client_operations = associated_client_operations
        self.associated_user_operations = associated_user_operations
        self.client_id = client_id
        self.elevated_operations = elevated_operations
        self.general_operations = general_operations
        self.linked_operations = linked_operations
        self.user_id = user_id
