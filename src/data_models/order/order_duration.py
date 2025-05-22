from enum import Enum


class OrderDuration(Enum):
    """
    Enum for order duration types.
    """

    SessionClose = "AtTheClose"
    SessionOpen = "AtTheOpening"
    DayOrder = "DayOrder"
    FillOrKill = "FillOrKill"
    GoodForPeriod = "GoodForPeriod"
    GoodTillCancel = "GoodTillCancel"
    GoodTillDate = "GoodTillDate"  # Requires a date in the body
    ImmediateOrCancel = "ImmediateOrCancel"

    def __str__(self):
        return self.value
