from enum import Enum


class PriceType(Enum):
    """
    Enum for price types.
    """

    PIP = "pip"
    PERCENT = "percent"
    PRICE = "price"

    def __str__(self):
        return self.value
        
    def __repr__(self):
        return self.value
