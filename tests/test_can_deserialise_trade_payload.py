import pytest

from data_models.trade_payload import MarketOrderTradePayload, LimitOrderTradePayload
from objects.price_type import PriceType
import json
from jsonschema.exceptions import ValidationError


def test_can_deserialise_market_order_trade_payload_from_json():
    json_payload = """
    {
        "quantity": 100000,
        "asset_type": "FxSpot",
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {
            "stop_loss": {
                "price": 1.1,
                "type": "pip"
            },
            "take_profit": {
                "price": 1.2,
                "type": "pip"
            }
        }
    }
    """

    deserialised_trade = MarketOrderTradePayload.from_json(json.loads(json_payload))

    assert deserialised_trade.quantity == 100000
    assert deserialised_trade.symbol == "EURUSD"
    assert deserialised_trade.side == "long"
    assert deserialised_trade.sl_tp.stop_loss.price == 1.1
    assert deserialised_trade.sl_tp.stop_loss.type == PriceType.PIP


@pytest.mark.parametrize("stop_price, take_price", [(-1.1, 1.2), (0.5, -0.6), (-1, -1)])
def test_cannot_deserialise_market_order_payload_with_negative_price(stop_price, take_price):
    json_payload = """
    {
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "long",
        "sl_tp": {
            "stop_loss": {
                "price": stop_price,
                "type": "pip"
            },
            "take_profit": {
                "price": take_price,
                "type": "pip"
            }
        }
    }
    """.replace("stop_price", str(stop_price)).replace("take_price", str(take_price))

    with pytest.raises(ValidationError):
        MarketOrderTradePayload.from_json(json.loads(json_payload))


@pytest.mark.parametrize("invalid_side", ["buy", "sell", "long_short", "l", "s"])
def test_cannot_deserialise_market_order_payload_with_invalid_side(invalid_side):
    json_payload = """
    {
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "invalid_side",
        "sl_tp": {
            "stop_loss": {
                "price": 1.1,
                "type": "pip"
            },
            "take_profit": {
                "price": 1.2,
                "type": "pip"
            }
        }
    }
    """.replace("invalid_side", invalid_side)

    with pytest.raises(ValidationError):
        MarketOrderTradePayload.from_json(json.loads(json_payload))


@pytest.mark.parametrize("quantity", [-1, 0, -100000])
def test_cannot_deserialise_market_order_payload_with_invalid_quantity(quantity):
    json_payload = f"""
    {{
        "quantity": {quantity},
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "pip"
            }},
            "take_profit": {{
                "price": 1.2,
                "type": "pip"
            }}
        }}
    }}
    """

    with pytest.raises(ValidationError):
        MarketOrderTradePayload.from_json(json.loads(json_payload))


def test_can_deserialise_limit_order_trade_payload_from_json():
    json_payload = """
    {
        "quantity": 100000,
        "asset_type": "FxSpot",
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {
            "stop_loss": {
                "price": 1.1,
                "type": "pip"
            },
            "take_profit": {
                "price": 1.2,
                "type": "pip"
            }
        },
        "limit_price": 1.3
    }
    """

    deserialised_trade = LimitOrderTradePayload.from_json(json.loads(json_payload))

    assert deserialised_trade.quantity == 100000
    assert deserialised_trade.symbol == "EURUSD"
    assert deserialised_trade.side == "long"
    assert deserialised_trade.sl_tp.stop_loss.price == 1.1
    assert deserialised_trade.sl_tp.stop_loss.type == PriceType.PIP
    assert deserialised_trade.limit_price == 1.3


@pytest.mark.parametrize("limit_price", [-1.1, -0.6, -1, -0.00001])
def test_cannot_deserialise_limit_order_payload_with_negative_limit_price(limit_price):
    json_payload = """
    {
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "long",
        "sl_tp": {
            "stop_loss": {
                "price": 1.1,
                "type": "pip"
            },
            "take_profit": {
                "price": 1.2,
                "type": "pip"
            }
        },
        "limit_price": replaceme
    }
    """.replace("replaceme", str(limit_price))

    with pytest.raises(
        ValidationError, match=r"Failed validating 'minimum' in schema\['properties'\]\['limit_price'\]"
    ):
        LimitOrderTradePayload.from_json(json.loads(json_payload))


@pytest.mark.parametrize("invalid_side", ["buy", "sell", "long_short", "l", "s"])
def test_cannot_deserialise_limit_order_payload_with_invalid_side(invalid_side):
    json_payload = f"""
    {{
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "{invalid_side}",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "pip"
            }},
            "take_profit": {{
                "price": 1.2,
                "type": "pip"
            }}
        }},
        "limit_price": 1.3
    }}
    """

    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json(json.loads(json_payload))


@pytest.mark.parametrize("quantity", [-1, 0, -100000])
def test_cannot_deserialise_limit_order_payload_with_invalid_quantity(quantity):
    json_payload = f"""
    {{
        "quantity": {quantity},
        "symbol": "EURUSD",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "pip"
            }},
            "take_profit": {{
                "price": 1.2,
                "type": "pip"
            }}
        }},
        "limit_price": 1.3
    }}
    """

    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json(json.loads(json_payload))


@pytest.mark.parametrize("invalid_price_type", ["invalid_type", "pips", "percentages"])
def test_cannot_deserialise_limit_order_payload_with_invalid_price_type(invalid_price_type):
    json_payload = f"""
    {{
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "{invalid_price_type}"
            }},
            "take_profit": {{
                "price": 1.2,
                "type": "pip"
            }}
        }},
        "limit_price": 1.3
    }}
    """

    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json(json.loads(json_payload))


@pytest.mark.parametrize("invalid_price_type", ["invalid_type", "pips", "%", "percentages", "s"])
def test_cannot_deserialise_market_order_payload_with_invalid_price_type(invalid_price_type):
    json_payload = f"""
    {{
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "side": "long",
        "sl_tp": {{
            "stop_loss": {{
                "price": 1.1,
                "type": "pip"
            }},
            "take_profit": {{
                "price": 1.2,
                "type": "{invalid_price_type}"
            }}
        }}
    }}
    """

    with pytest.raises(ValidationError):
        MarketOrderTradePayload.from_json(json.loads(json_payload))


def test_cannot_deserialise_invalid_json_for_limit_order_payload():
    invalid_json_payload = """
    {
        "quantity": 100000,
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "something_else": "invalid",
        "side": "long",
        "sl_tp": {
            "stop_loss": {
                "price": 1.1,
                "type": "pip"
            },
            "take_profit": {
                "price": 1.2,
                "type": "pip"
            }
        },
        "limit_price": 1.3
    }
    """

    with pytest.raises(ValidationError, match=r"'something_else' was unexpected"):
        LimitOrderTradePayload.from_json(invalid_json_payload)
