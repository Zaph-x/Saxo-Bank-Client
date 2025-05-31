
class HistoricalPosition:
    def __init__(self, data):
        self.net_position_id = data.get("NetPositionId", "")
        closed_position = data.get("ClosedPosition", {})
        self.position_id = closed_position.get("PositionId", "")
        self.uic = closed_position.get("Uic", 0)
        self.asset_type = closed_position.get("AssetType", "")
        self.amount = closed_position.get("Amount", 0)
        self.open_price = closed_position.get("OpenPrice", 0.0)
        self.cost_opening = closed_position.get("CostOpening", 0.0)
        self.cost_opening_in_currency = closed_position.get("CostOpeningInBaseCurrency", "")
        self.closing_price = closed_position.get("ClosingPrice", 0.0)
        self.closing_method = closed_position.get("ClosingMethod", "")
        self.cost_closing = closed_position.get("CostClosing", 0.0)
        self.cost_closing_in_currency = closed_position.get("CostClosingInBaseCurrency", "")
        self.direction = closed_position.get("BuyOrSell", "")
        self.open_time = closed_position.get("ExecutionTimeOpen", "")
        self.close_time = closed_position.get("ExecutionTimeClose", "")
        self.pnl = closed_position.get("ClosedProfitLoss", 0.0)
        self.pnl_in_currency = closed_position.get("ClosedProfitLossInBaseCurrency", "")
        self.conv_rate_to_base_settled = closed_position.get("ConversionRateInstrumentToBaseSettledClosing", False)
        self.conv_rate_to_base_open = closed_position.get("ConversionRateInstrumentToBaseSettledOpening", False)

    def to_json(self):
        return {
            "NetPositionId": self.net_position_id,
            "PositionId": self.position_id,
            "Uic": self.uic,
            "AssetType": self.asset_type,
            "Amount": self.amount,
            "OpenPrice": self.open_price,
            "ClosingPrice": self.closing_price,
            "ClosingMethod": self.closing_method,
            "Direction": self.direction,
            "ExecutionTimeOpen": self.open_time,
            "ExecutionTimeClose": self.close_time,
            "ClosedProfitLoss": self.pnl,
            "ClosedProfitLossInBaseCurrency": self.pnl_in_currency,
            "ConversionRateInstrumentToBaseSettledClosing": self.conv_rate_to_base_settled,
            "ConversionRateInstrumentToBaseSettledOpening": self.conv_rate_to_base_open
        }

