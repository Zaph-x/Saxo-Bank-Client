from data_models.json_model_base import JsonModelBase


class RelatedOrOcoOrderModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "OrderId": {"type": "string"},
        },
        "required": ["OrderId"],
    }

    def __init__(
        self: "RelatedOrOcoOrderModel",
        order_id: str,
    ) -> None:
        self.order_id = order_id
