from utils.price import calculate_stop_loss, calculate_take_profit
import math
from data_models.trade_payload import MarketOrderTradePayload, StopLossTakeProfitPayload
from data_models.trading.stop_loss import StopLoss
from data_models.trading.take_profit import TakeProfit
from data_models.trading.asset_type import AssetType
import pytest
import json

from data_models.price.price_info import PriceInfo
from data_models.price.price_type import PriceType


def create_price_info(bid, ask):
    return PriceInfo(
        {
            "Quote": {"Bid": bid, "Ask": ask, "Mid": (bid + ask) / 2, "DelayedByMinutes": 0, "MarketState": "Open"},
            "LastUpdated": "2023-10-01T12:00:00.000Z",
            "AssetType": AssetType.FxSpot,
            "Uic": 123456,
            "DisplayAndFormat": {
                "Symbol": "EUR/USD",
                "OrderDecimals": 5,
                "Format": "AllowDecimalPips",
                "Currency": "USD",
            },
        }
    )


@pytest.mark.parametrize(
    "bid, ask, price, expected",
    [(1.1, 1.2, 1.3, 1.3), (1.5, 1.6, 1.7, 1.7), (2.0, 2.1, 2.2, 2.2), (0.9, 1.0, 1.1, 1.1), (0.5, 0.6, 0.7, 0.7)],
)
def test_calculate_take_profit_calculates_correct_price(bid, ask, price, expected):
    price_info = create_price_info(bid, ask)
    json_payload = f"""
    {{
        "quantity": 100000,
        "asset_type": "FxSpot",
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "price"
            }},
            "take_profit": {{
                "price": {price},
                "type": "price"
            }}
        }}
    }}
    """

    order = MarketOrderTradePayload.from_json(json.loads(json_payload))

    result = calculate_take_profit(price_info, order, .0001)
    assert result == expected, f"Expected {expected}, but got {result} for price {price} with bid {bid} and ask {ask}"


@pytest.mark.parametrize(
    "bid, ask, price, expected",
    [
        (1000, 2000, 10, 2200),
        (0.5, 1.0, 10, 1.1),
        (1.0, 2.0, 10, 2.2),
    ],
)
def test_calculate_take_profit_calculates_correct_price_for_percentages(bid, ask, price, expected):
    price_info = create_price_info(bid, ask)
    json_payload = f"""
    {{
        "quantity": 100000,
        "asset_type": "FxSpot",
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "percent"
            }},
            "take_profit": {{
                "price": {price},
                "type": "percent"
            }}
        }}
    }}
    """

    order = MarketOrderTradePayload.from_json(json.loads(json_payload))

    result = calculate_take_profit(price_info, order, .1)
    assert result == expected, f"Expected {expected}, but got {result} for price {price} with bid {bid} and ask {ask}"


@pytest.mark.parametrize(
    "bid, ask, price",
    [
        (1.1, 1.2, -1),
        (1.5, 1.6, -10),
        (2.0, 2.1, -100),
        (0.9, 1.0, -0.5),
        (0.5, 0.6, -0.1),
        (1.0, 2.0, -0.01),
        (1.0, 2.0, -0.001),
        (1.0, 2.0, -0.0001),
        (1.0, 2.0, -0.00001),
        (1.0, 2.0, -0.000001),
        (1.0, 2.0, -0.0000001),
        (1.0, 2.0, -0.00000001),
        (1.2, 1.3, -math.inf),
        (1.0, 2.0, -0.000000001),
        (1.2, 1.3, 0),
    ],
)
def test_calculate_take_profit_cannot_calculate_for_negative_or_zero_price(bid, ask, price):
    price_info = create_price_info(bid, ask)
    order = MarketOrderTradePayload(
        "EURUSD",
        AssetType.FxSpot.value,
        100000,
        "long",
        StopLossTakeProfitPayload(
            StopLoss(price=1.1, type=PriceType.PERCENT), TakeProfit(price=price, type=PriceType.PERCENT)
        ),
    )

    with pytest.raises(ValueError) as excinfo:
        calculate_take_profit(price_info, order,1)
    assert str(excinfo.value) == f"Take profit price must be above 0: {price}"


@pytest.mark.parametrize(
    "bid, ask, price, expected",
    [(1.1, 1.2, 1.3, 1.3), (1.5, 1.6, 1.7, 1.7), (2.0, 2.1, 2.2, 2.2), (0.9, 1.0, 1.1, 1.1), (0.5, 0.6, 0.7, 0.7)],
)
def test_calculate_stop_loss_calculates_correct_price(bid, ask, price, expected):
    price_info = create_price_info(bid, ask)
    json_payload = f"""
    {{
        "quantity": 100000,
        "asset_type": "FxSpot",
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": {price},
                "type": "price"
            }},
            "take_profit": {{
                "price": 1.5,
                "type": "price"
            }}
        }}
    }}
    """

    order = MarketOrderTradePayload.from_json(json.loads(json_payload))

    result = calculate_stop_loss(price_info, order, .1)
    assert result == expected, f"Expected {expected}, but got {result}"


@pytest.mark.parametrize(
    "bid, ask, price, expected",
    [(1.1, 1.2, 10, 1.08), (0.5, 1.0, 10, 0.9), (1.0, 2.0, 10, 1.8), (1000, 2000, 10, 1800), (0.5, 0.6, 10, 0.54)],
)
def test_calculate_stop_loss_calculates_correct_price_for_percentages(bid, ask, price, expected):
    price_info = create_price_info(bid, ask)
    json_payload = f"""
    {{
        "quantity": 100000,
        "asset_type": "FxSpot",
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": {price},
                "type": "percent"
            }},
            "take_profit": {{
                "price": 1.5,
                "type": "percent"
            }}
        }}
    }}
    """

    order = MarketOrderTradePayload.from_json(json.loads(json_payload))

    result = calculate_stop_loss(price_info, order, .01)
    assert result == expected, f"Expected {expected}, but got {result}"


@pytest.mark.parametrize(
    "bid, ask, price",
    [
        (1.1, 1.2, -1),
        (1.5, 1.6, -10),
        (2.0, 2.1, -100),
        (0.9, 1.0, -0.5),
        (0.5, 0.6, -0.1),
        (1.0, 2.0, -0.01),
        (1.0, 2.0, -0.001),
        (1.0, 2.0, -0.0001),
        (1.0, 2.0, -0.00001),
        (1.0, 2.0, -0.000001),
        (1.0, 2.0, -0.0000001),
        (1.0, 2.0, -0.00000001),
        (1.0, 2.0, -0.000000001),
        (1.2, 1.3, 0),
        (1.2, 1.3, -math.inf),
    ],
)
def test_calculate_stop_loss_cannot_calculate_for_negative_or_zero_price(bid, ask, price):
    price_info = create_price_info(bid, ask)
    order = MarketOrderTradePayload(
        "EURUSD",
        AssetType.FxSpot.value,
        100000,
        "long",
        StopLossTakeProfitPayload(
            StopLoss(price=price, type=PriceType.PERCENT), TakeProfit(price=1.1, type=PriceType.PERCENT)
        ),
    )

    with pytest.raises(ValueError) as excinfo:
        calculate_stop_loss(price_info, order, .1)
    assert str(excinfo.value) == f"Stop loss price must be above 0: {price}"
