from datetime import datetime


class PriceInfo:
    def __init__(self, data: dict):
        self.bid = data["Quote"]["Bid"]
        self.mid = data["Quote"]["Mid"]
        self.ask = data["Quote"]["Ask"]
        self.delayed_by = data["Quote"]["DelayedByMinutes"]
        self.market_state = data["Quote"]["MarketState"]
        self.last_update = datetime.strptime(data["LastUpdated"], "%Y-%m-%dT%H:%M:%S.%fZ")
        self.asset_type = data["AssetType"]
        self.uic = data["Uic"]
        self.symbol = data["DisplayAndFormat"]["Symbol"]
        self.order_decimals = data["DisplayAndFormat"]["OrderDecimals"]
        self.allow_decimal_pips = data["DisplayAndFormat"]["Format"] == "AllowDecimalPips"
        self.currency = data["DisplayAndFormat"]["Currency"]

    def get_decimal_size(self):
        """
        Returns the decimal size for the price.
        """
        if self.allow_decimal_pips:
            return self.order_decimals + 1
        return self.order_decimals
        
    def to_json(self):
        """
        Converts the price information to a dictionary for JSON serialization.
        """
        return {
            "bid": self.bid,
            "mid": self.mid,
            "ask": self.ask,
            "delayed_by_minutes": self.delayed_by,
            "market_state": self.market_state,
            "last_update": self.last_update.isoformat(),
            "asset_type": self.asset_type,
            "uic": self.uic,
            "symbol": self.symbol,
            "order_decimals": self.order_decimals,
            "allow_decimal_pips": self.allow_decimal_pips,
            "currency": self.currency
        }
