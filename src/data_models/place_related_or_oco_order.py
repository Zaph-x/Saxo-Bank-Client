from data_models.json_model_base import JsonModelBase


class PlaceRelatedOrOcoOrderModel(JsonModelBase):
    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "AccountKey": {"type": "string"},
            "Amount": {"type": "number"},
            "AssetType": {"type": "string"},
            "BuySell": {"enum": ["Buy", "Sell"]},
            "OrderDuration": {"type": "object", "properties": {"OrderDurationType": {"type": "string", "enum": []}}},
            "OrderType": {"type": "string"},
            "OrderPrice": {"type": "number"},
            "Uid": {"type": "number"},
            "AmountType": {"type": ["string", "null"], "enum": ["Quantity", "CashAmount"]},
        },
        "required": ["AccountKey", "Amount", "AssetType", "BuySell", "OrderDuration", "OrderType", "Uid"],
    }

    def __init__(
        self,
        AccountKey: str,
        Amount: float,
        AssetType: str,
        BuySell: str,
        OrderDuration: dict,
        OrderType: str,
        OrderPrice: float,
        Uid: int,
        AmountType: str = "Quantity",
    ):
        """
        Args:
            AccountKey (str): The account key.
            Amount (float): The amount of the order.
            AssetType (str): The type of asset.
            BuySell (str): "Buy" or "Sell".
            OrderDuration (dict): The duration of the order.
            OrderType (str): The type of order.
            OrderPrice (float): The price of the order.
            Uid (int): The unique identifier for the order.
        """
        super().__init__()
        self.AccountKey = AccountKey
        self.Amount = Amount
        self.AmountType = AmountType
        self.AssetType = AssetType
        self.BuySell = BuySell
        self.OrderDuration = OrderDuration
        self.OrderType = OrderType
        self.OrderPrice = OrderPrice
        self.Uid = Uid
