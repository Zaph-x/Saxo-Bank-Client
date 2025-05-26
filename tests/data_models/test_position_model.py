from data_models.saxo.position import PositionModel

def test_can_get_positon_model_from_dict():
    pos = {'NetPositionId': 'EURUSD__FxSpot', 'PositionBase': {'AccountId': '20072172', 'AccountKey': 'rY4V9sg54wXk8MD3JpAYLw==', 'Amount': 10000.0, 'AssetType': 'FxSpot', 'CanBeClosed': True, 'ClientId': '20072172', 'CloseConversionRateSettled': False, 'CorrelationKey': '1a952ae1-1ac9-47b6-bc96-c18ee588b13d', 'ExecutionTimeOpen': '2025-05-21T18:10:07.580201Z', 'IsForceOpen': False, 'IsMarketOpen': True, 'LockedByBackOffice': False, 'OpenBondPoolFactor': 1.0, 'OpenPrice': 1.13495, 'OpenPriceIncludingCosts': 1.13525, 'OpenSwap': 0.00033, 'RelatedOpenOrders': [], 'SourceOrderId': '5035032895', 'SpotDate': '2025-05-23', 'Status': 'Open', 'Uic': 21, 'ValueDate': '2025-05-27T00:00:00.000000Z'}, 'PositionId': '5023647477', 'PositionView': {'Ask': 1.1362, 'Bid': 1.136, 'CalculationReliability': 'Ok', 'ConversionRateCurrent': 0.8802005, 'ConversionRateOpen': 0.88255, 'CurrentBondPoolFactor': 1.0, 'CurrentPrice': 1.136, 'CurrentPriceDelayMinutes': 0, 'CurrentPriceType': 'Bid', 'Exposure': 10000.0, 'ExposureCurrency': 'EUR', 'ExposureInBaseCurrency': 10000.0, 'InstrumentPriceDayPercentChange': 0.72, 'MarketState': 'Open', 'MarketValue': 10.5, 'MarketValueInBaseCurrency': 9.24, 'ProfitLossOnTrade': 10.5, 'ProfitLossOnTradeInBaseCurrency': 9.24, 'ProfitLossOnTradeIntraday': 80.4, 'ProfitLossOnTradeIntradayInBaseCurrency': 70.7, 'TradeCostsTotal': -6.0, 'TradeCostsTotalInBaseCurrency': -5.29}}

    position_model = PositionModel(pos)

    assert position_model.net_position_id == 'EURUSD__FxSpot'
    assert position_model.position_id == '5023647477'
    assert position_model.amount == 10000.0
    assert position_model.execution_time == '2025-05-21T18:10:07.580201Z'
    assert position_model.locked_by_backoffice is False
    assert position_model.uic == 21
    assert position_model.status == 'Open'
    assert position_model.is_market_open is True
    assert position_model.can_be_closed is True
    assert position_model.open_price == 1.13495
    assert position_model.position_view.ask_price == 1.1362
    assert position_model.position_view.bid_price == 1.136
    assert position_model.position_view.calculation_reliability == 'Ok'
    assert position_model.position_view.current_price == 1.136
    assert position_model.position_view.current_price_type == 'Bid'
    assert position_model.position_view.current_price_delay_minutes == 0
    assert position_model.position_view.exposure == 10000.0
    assert position_model.position_view.exposure_currency == 'EUR'
    assert position_model.position_view.pnl == 10.5
    assert position_model.position_view.pnl_in_currency == 9.24
    assert position_model.position_view.instrument_price_day_percent_change == 0.72
    assert position_model.position_view.trade_costs == -6.0
    assert position_model.position_view.trade_costs_in_currency == -5.29
    assert position_model.position_view.pnl_intraday == 80.4
    assert position_model.position_view.pnl_intraday_in_currency == 70.7

