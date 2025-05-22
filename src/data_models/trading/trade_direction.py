from enum import Enum


class TradeDirection(Enum):
    """
    Enum for trade direction.

    LONG: Represents a long position (buy).
    SHORT: Represents a short position (sell).
    """

    LONG = "Buy"
    SHORT = "Sell"
    SELL = "Sell"
    BUY = "Buy"

    def __str__(self):
        return self.name
