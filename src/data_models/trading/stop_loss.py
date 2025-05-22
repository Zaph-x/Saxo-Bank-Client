from data_models.price.price_type import PriceType
from data_models.json_model_base import JsonModelBase


class StopLoss(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "type": {"type": "string", "enum": ["pip", "percent", "price"]},
            "price": {"type": "number", "minimum": 0},
        },
        "required": ["type", "price"],
    }

    def __init__(self, type: PriceType | str, price: float):
        """
        Initialize the StopLoss object.

        Args:
            type (PriceType | str): The type of price (e.g., "pip", "percent", "price").
            price (float): The price value.
        """
        self.type = PriceType(type) if isinstance(type, str) else type
        self.price = price

    def calculate_price(self):
        """
        Calculate the stop loss price based on the price type and value.

        Returns:
            float: The calculated take profit price.
        """
        if self.type == PriceType.PIP:
            raise NotImplementedError("PIP calculation is not implemented.")
        elif self.type == PriceType.PERCENT:
            return self.price / 100
        elif self.type == PriceType.PRICE:
            return self.price
        else:
            raise ValueError(f"Invalid price type: {self.type}")

    def _validate(self):
        """
        Validate the StopLoss object.

        Raises:
            ValueError: If the price type is invalid or the price is not a number.
        """
        if not isinstance(self.price, (int, float)):
            raise ValueError("Invalid price. Must be a number.")
        if self.type not in [PriceType.PIP, PriceType.PERCENT, PriceType.PRICE]:
            raise ValueError(f"Invalid price type: {self.type}")
