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
