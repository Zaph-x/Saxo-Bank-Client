
class PositionView:
    def __init__(self, data):
        self.ask_price = data.get("Ask", 0.)
        self.bid_price = data.get("Bid", 0.)
        self.calculation_reliability = data.get("CalculationReliability", "")
        self.current_price = data.get("CurrentPrice", 0.)
        self.current_price_type = data.get("CurrentPriceType", "")
        self.current_price_delay_minutes = data.get("CurrentPriceDelayMinutes", 0)
        self.exposure = data.get("Exposure", 0.)
        self.exposure_currency = data.get("ExposureCurrency", "")
        self.pnl = data.get("ProfitLossOnTrade", 0.)
        self.pnl_in_currency = data.get("ProfitLossOnTradeInBaseCurrency", "")
        self.instrument_price_day_percent_change = data.get("InstrumentPriceDayPercentChange", 0.)
        self.trade_costs = data.get("TradeCostsTotal", 0.)
        self.trade_costs_in_currency = data.get("TradeCostsTotalInBaseCurrency", 0.)
        self.pnl_intraday = data.get("ProfitLossOnTradeIntraday", 0.)
        self.pnl_intraday_in_currency = data.get("ProfitLossOnTradeIntradayInBaseCurrency", 0.)

    def to_json(self):
        return {
            "Ask": self.ask_price,
            "Bid": self.bid_price,
            "CalculationReliability": self.calculation_reliability,
            "CurrentPrice": self.current_price,
            "CurrentPriceType": self.current_price_type,
            "CurrentPriceDelayMinutes": self.current_price_delay_minutes,
            "Exposure": self.exposure,
            "ExposureCurrency": self.exposure_currency,
            "PnlOnTrade": self.pnl,
            "PnlOnTradeInBaseCurrency": self.pnl_in_currency,
            "PnlOnTradeIntraday": self.pnl_intraday,
            "PnlOnTradeIntradayInBaseCurrency": self.pnl_intraday_in_currency,
            "InstrumentPriceDayPercentChange": self.instrument_price_day_percent_change,
            "TradeCosts": self.trade_costs,
            "TradeCostsInBaseCurrency": self.trade_costs_in_currency,
        }


class PositionModel:
    def __init__(self, data):
        self.net_position_id = data.get("NetPositionId", "")
        self.position_id = data.get("PositionId", "")
        self.amount = data.get("PositionBase", {}).get("Amount", 0)
        self.execution_time = data.get("PositionBase", {}).get("ExecutionTimeOpen", "")
        self.locked_by_backoffice = data.get("PositionBase", {}).get("LockedByBackOffice", False)
        self.uic = data.get("PositionBase", {}).get("Uic", 0)
        self.status = data.get("PositionBase", {}).get("Status", "")
        self.is_market_open = data.get("PositionBase", {}).get("IsMarketOpen", False)
        self.can_be_closed = data.get("PositionBase", {}).get("CanBeClosed", False)
        self.open_price = data.get("PositionBase", {}).get("OpenPrice", 0)
        self.position_view = PositionView(data.get("PositionView", {}))


    def to_json(self):
        return {
            "NetPositionId": self.net_position_id,
            "PositionId": self.position_id,
            "Amount": self.amount,
            "IsMarketOpen": self.is_market_open,
            "ExecutionTimeOpen": self.execution_time,
            "CanBeClosed": self.can_be_closed,
            "LockedByBackOffice": self.locked_by_backoffice,
            "Uic": self.uic,
            "Status": self.status,
            "OpenPrice": self.open_price,
            "PositionView": self.position_view.to_json(),
        }
