class BalanceInformation:
    def __init__(self, data: dict) -> None:
        """
        Initialize the BalanceInformation object with data.

        Args:
            data (dict): The balance information data.
        """
        self._data = data
        self.cash_balance = data.get("CashBalance", 0)
        self.Currency = data.get("Currency", "")
        self.total_value = data.get("TotalValue", 0)
        self.margin_available = data.get("MarginAvailableForTrading", 0)
        self.net_positions_count = data.get("NetPositionsCount", 0)
        self.orders_count = data.get("OrdersCount", 0)

    def to_json(self) -> dict:
        """
        Convert the balance information to JSON format.

        Returns:
            dict: The balance information in JSON format.
        """
        return {
            "CashBalance": self.cash_balance,
            "Currency": self.Currency,
            "TotalValue": self.total_value,
            "MarginAvailableForTrading": self.margin_available,
            "NetPositionsCount": self.net_positions_count,
            "OrdersCount": self.orders_count,
        }

    def get_property(self, key: str):
        """
        Get the value of a specific property from the balance information.

        Args:
            key (str): The key of the property to retrieve.

        Returns:
            The value of the specified property, or None if it doesn't exist.
        """
        return self._data.get(key)
