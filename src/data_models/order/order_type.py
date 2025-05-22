from enum import Enum


class OrderType(Enum):
    Limit = "Limit"
    Market = "Market"
    Stop = "Stop"
    StopLimit = "StopLimit"
    TrailingStop = "TrailingStop"

    def __str__(self):
        return self.value
