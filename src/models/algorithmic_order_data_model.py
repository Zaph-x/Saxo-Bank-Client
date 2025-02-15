from models.json_model_base import JsonModelBase

class AlgorithmnicOrderDataModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "Arguments": {"type": "object", "properties": {"type": "string"}},
            "StrategyName": {"type": "string"},
        },
        "required": ["Arguments", "StrategyName"],
    }

    def __init__(
        self: "AlgorithmnicOrderDataModel",
        arguments: dict[str, str],
        strategy_name: str,
    ) -> None:
        self.arguments = arguments
        self.strategy_name = strategy_name
