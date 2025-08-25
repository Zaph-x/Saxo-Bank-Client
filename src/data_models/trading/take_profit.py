from data_models.price.price_type import PriceType
from data_models.json_model_base import JsonModelBase


class TakeProfit(JsonModelBase):
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
        Initialize the TakeProfit object.

        Args:
            type (PriceType | str): The type of price (e.g., "pip", "percent", "price").
            price (float): The price value.
        """
        self.type = PriceType(type) if isinstance(type, str) else type
        self.price = price

    def calculate_price(self):
        """
        Calculate the take profit price based on the price type and value.

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

    def __str__(self):
        return f"TakeProfit(type={self.type}, price={self.price})"

    def __repr__(self):
        return self.__str__()
