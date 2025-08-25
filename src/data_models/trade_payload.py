from data_models.trading.take_profit import TakeProfit
from data_models.trading.stop_loss import StopLoss
from data_models.json_model_base import JsonModelBase
from data_models.trading.asset_type import AssetType

from typing import Optional


class StopLossTakeProfitPayload(JsonModelBase):
    """
    Represents a payload for stop loss and take profit settings.
    This class is used to create a stop loss and take profit payload with the specified parameters.

    Attributes:
        stop_loss (StopLoss): The stop loss settings.
        take_profit (TakeProfit): The take profit settings.
    """

    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "stop_loss": {"type": "object"},
            "take_profit": {"type": "object"},
        },
        "required": ["stop_loss", "take_profit"],
    }

    def __init__(self, stop_loss: dict | StopLoss, take_profit: dict | TakeProfit):
        self.stop_loss = StopLoss.from_json(stop_loss) if isinstance(stop_loss, dict) else stop_loss
        self.take_profit = TakeProfit.from_json(take_profit) if isinstance(take_profit, dict) else take_profit

    def __str__(self):
        return f"StopLossTakeProfitPayload(stop_loss={self.stop_loss}, take_profit={self.take_profit})"

    def __repr__(self):
        return self.__str__()

class MarketOrderTradePayload(JsonModelBase):
    """
    Represents a trade payload for creating a order.

    This class is used to create a trade order with the specified parameters.
    It includes the symbol, quantity, side (long or short), stop loss and take profit settings.

    Attributes:
        symbol (str): The symbol for the trade.
        quantity (int): The quantity of the trade.
        side (str): The side of the trade ('long' or 'short').
        sl_tp (StopLossTakeProfitPayload): The stop loss and take profit payload.
    """

    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "properties": {
            "symbol": {"type": "string"},
            "asset_type": {"type": "string", "enum": [asset.value for asset in AssetType]},
            "quantity": {"type": "integer", "minimum": 1},
            "side": {"type": "string", "enum": ["long", "short"]},
            "sl_tp": {"type": "object"},
            "algo_name": {"type": "string"},
        },
        "required": ["symbol", "quantity","asset_type", "side", "sl_tp"],
    }

    def __init__(
        self,
        symbol: str,
        asset_type: str,
        quantity: int,
        side: str,
        sl_tp: StopLossTakeProfitPayload,
        algo_name: Optional[str] = None,
    ):
        self.symbol = symbol
        self.asset_type = AssetType(asset_type)
        self.quantity = quantity
        self.side = side
        self.algo_name = algo_name
        self.sl_tp = (
            StopLossTakeProfitPayload.from_json(sl_tp) if isinstance(sl_tp, str) or isinstance(sl_tp, dict) else sl_tp
        )

    def __str__(self):
        return f"MarketOrderTradePayload(symbol={self.symbol}, quantity={self.quantity}, side={self.side}, sl_tp={self.sl_tp})"

    def __repr__(self):
        return self.__str__()


class LimitOrderTradePayload(JsonModelBase):
    """
    Represents a trade payload for creating a limit order.

    This class is used to create a limit order with the specified parameters.
    It includes the symbol, quantity, side (long or short), stop loss and take profit settings, and limit price.

    Attributes:
        symbol (str): The symbol for the trade.
        quantity (int): The quantity of the trade.
        side (str): The side of the trade ('long' or 'short').
        sl_tp (StopLossTakeProfitPayload): The stop loss and take profit payload.
        limit_price (float): The limit price for the order.
    """

    __schema__ = {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "symbol": {"type": "string"},
            "asset_type": {"type": "string", "enum": [asset.value for asset in AssetType]},
            "quantity": {"type": "integer", "minimum": 1},
            "side": {"type": "string", "enum": ["long", "short"]},
            "sl_tp": {"type": "object"},
            "limit_price": {"type": "number", "minimum": 0},
            "algo_name": {"type": "string"},
        },
        "required": ["symbol", "quantity", "side", "sl_tp", "limit_price"],
    }

    def __init__(
        self,
        symbol: str,
        asset_type: str,
        quantity: int,
        side: str,
        sl_tp: StopLossTakeProfitPayload,
        limit_price: float,
        algo_name: Optional[str] = None,
    ):
        self.symbol = symbol
        self.asset_type = AssetType(asset_type)
        self.quantity = quantity
        self.side = side
        self.sl_tp = (
            StopLossTakeProfitPayload.from_json(sl_tp) if isinstance(sl_tp, str) or isinstance(sl_tp, dict) else sl_tp
        )
        self.limit_price = limit_price
        self.algo_name = algo_name

    def __str__(self):
        return f"LimitOrderTradePayload(symbol={self.symbol}, quantity={self.quantity}, side={self.side}, sl_tp={self.sl_tp}, limit_price={self.limit_price})"

    def __repr__(self):
        return self.__str__()
