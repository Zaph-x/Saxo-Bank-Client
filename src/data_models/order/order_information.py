from dateutil.parser import isoparse
from data_models.order.order_type import OrderType
from data_models.order.order_duration import OrderDuration
from data_models.trading.trade_direction import TradeDirection


class OrderInformation:
    def __init__(self, data: dict):
        """
        Initializes the OrderInformation class with order data.

        Args:
            data (dict): A dictionary containing order information.
        """
        self._data = data
        self.order_id = data.get("OrderId", "")
        self.amount = data.get("Amount", 0)
        self.friendly_name = data.get("DisplayAndFormat", dict()).get("Description", "")
        self.symbol = data.get("DisplayAndFormat", dict()).get("Symbol", "")
        self.order_type = OrderType(data.get("OpenOrderType", ""))
        self.order_relation = data.get("OrderRelation", "")
        self.uic = data.get("Uic", -1)
        self.asset_type = data.get("AssetType", "")
        self.order_time = isoparse(data.get("OrderTime", ""))
        self.trade_direction = TradeDirection(data.get("BuySell", ""))
        self.duration = OrderDuration(data.get("Duration", dict()).get("DurationType", ""))
        self.price = data.get("Price", 0)

    def __str__(self):
        """
        Returns a string representation of the OrderInformation object.

        Returns:
            str: A string representation of the order information.
        """
        return f"Order ID: {self.order_id}, Amount: {self.amount}, Symbol: {self.symbol}, Price: {self.price}"

    def __repr__(self):
        """
        Returns a string representation of the OrderInformation object for debugging.

        Returns:
            str: A string representation of the order information for debugging.
        """
        return f"OrderInformation({self.__str__()})"
