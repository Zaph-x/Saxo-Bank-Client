from models.json_model_base import JsonModelBase

class PlaceRelatedOrOcoOrderModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "AlgorithmicOrderData": {"type": "object"},
            "RelatedOrOcoOrder": {"type": "object"},
        },
        "required": ["AlgorithmicOrderData", "RelatedOrOcoOrder"],
    }

