import pytest
import json
from jsonschema.exceptions import ValidationError
from data_models.trade_payload import LimitOrderTradePayload, StopLossTakeProfitPayload
from data_models.trading.stop_loss import StopLoss
from data_models.trading.take_profit import TakeProfit
from data_models.price.price_type import PriceType
from data_models.trading.asset_type import AssetType


def test_limit_order_trade_payload_init_with_objects():
    """Test initialization with StopLossTakeProfitPayload object."""
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    take_profit = TakeProfit(type=PriceType.PIP, price=2.5)
    sl_tp = StopLossTakeProfitPayload(stop_loss=stop_loss, take_profit=take_profit)
    
    payload = LimitOrderTradePayload(
        symbol="EURUSD",
        asset_type="FxSpot",
        quantity=100000,
        side="long",
        sl_tp=sl_tp,
        limit_price=1.3,
        algo_name="TestAlgo"
    )
    
    assert payload.symbol == "EURUSD"
    assert payload.asset_type == AssetType.FxSpot
    assert payload.quantity == 100000
    assert payload.side == "long"
    assert payload.sl_tp is sl_tp
    assert payload.limit_price == 1.3
    assert payload.algo_name == "TestAlgo"


def test_limit_order_trade_payload_init_with_dict():
    """Test initialization with dictionary for sl_tp."""
    sl_tp_dict = {
        "stop_loss": {"type": "pip", "price": 1.5},
        "take_profit": {"type": "pip", "price": 2.5}
    }
    
    payload = LimitOrderTradePayload(
        symbol="EURUSD",
        asset_type="FxSpot",
        quantity=100000,
        side="long",
        sl_tp=sl_tp_dict,
        limit_price=1.3
    )
    
    assert payload.symbol == "EURUSD"
    assert payload.asset_type == AssetType.FxSpot
    assert payload.quantity == 100000
    assert payload.side == "long"
    assert isinstance(payload.sl_tp, StopLossTakeProfitPayload)
    assert payload.sl_tp.stop_loss.price == 1.5
    assert payload.sl_tp.take_profit.price == 2.5
    assert payload.limit_price == 1.3
    assert payload.algo_name is None


def test_limit_order_trade_payload_to_json():
    """Test serializing to JSON."""
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    take_profit = TakeProfit(type=PriceType.PIP, price=2.5)
    sl_tp = StopLossTakeProfitPayload(stop_loss=stop_loss, take_profit=take_profit)
    
    payload = LimitOrderTradePayload(
        symbol="EURUSD",
        asset_type="FxSpot",
        quantity=100000,
        side="long",
        sl_tp=sl_tp,
        limit_price=1.3,
        algo_name="TestAlgo"
    )
    
    json_str = payload.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["symbol"] == "EURUSD"
    assert json_dict["assetType"] == "FxSpot"
    assert json_dict["quantity"] == 100000
    assert json_dict["side"] == "long"
    assert json_dict["slTp"]["stopLoss"]["price"] == 1.5
    assert json_dict["slTp"]["stopLoss"]["type"] == "pip"
    assert json_dict["slTp"]["takeProfit"]["price"] == 2.5
    assert json_dict["slTp"]["takeProfit"]["type"] == "pip"
    assert json_dict["limitPrice"] == 1.3
    assert json_dict["algoName"] == "TestAlgo"


def test_limit_order_trade_payload_from_json_with_dict():
    """Test deserializing from JSON dict."""
    json_dict = {
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "quantity": 100000,
        "side": "long",
        "sl_tp": {
            "stop_loss": {"type": "pip", "price": 1.5},
            "take_profit": {"type": "pip", "price": 2.5}
        },
        "limit_price": 1.3,
        "algo_name": "TestAlgo"
    }
    
    payload = LimitOrderTradePayload.from_json(json_dict)
    
    assert payload.symbol == "EURUSD"
    assert payload.asset_type == AssetType.FxSpot
    assert payload.quantity == 100000
    assert payload.side == "long"
    assert isinstance(payload.sl_tp, StopLossTakeProfitPayload)
    assert payload.sl_tp.stop_loss.price == 1.5
    assert payload.sl_tp.stop_loss.type == PriceType.PIP
    assert payload.sl_tp.take_profit.price == 2.5
    assert payload.sl_tp.take_profit.type == PriceType.PIP
    assert payload.limit_price == 1.3
    assert payload.algo_name == "TestAlgo"


def test_limit_order_trade_payload_from_json_without_algo_name():
    """Test deserializing from JSON without algo_name."""
    json_dict = {
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "quantity": 100000,
        "side": "long",
        "sl_tp": {
            "stop_loss": {"type": "pip", "price": 1.5},
            "take_profit": {"type": "pip", "price": 2.5}
        },
        "limit_price": 1.3
    }
    
    payload = LimitOrderTradePayload.from_json(json_dict)
    
    assert payload.symbol == "EURUSD"
    assert payload.asset_type == AssetType.FxSpot
    assert payload.quantity == 100000
    assert payload.side == "long"
    assert isinstance(payload.sl_tp, StopLossTakeProfitPayload)
    assert payload.limit_price == 1.3
    assert payload.algo_name is None


def test_limit_order_trade_payload_validate_required_fields():
    """Test validation for required fields."""
    # Missing symbol
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "quantity": 100000,
            "asset_type": "FxSpot",
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })

    # Missing quantity
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })

    # Missing side
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 100000,
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })

    # Missing sl_tp
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 100000,
            "side": "long",
            "limit_price": 1.3
        })
        
    # Missing limit_price
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 100000,
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            }
        })


def test_limit_order_trade_payload_validate_negative_quantity():
    """Test validation fails with negative quantity."""
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": -100000,
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })


def test_limit_order_trade_payload_validate_zero_quantity():
    """Test validation fails with zero quantity."""
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 0,
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })


def test_limit_order_trade_payload_validate_invalid_side():
    """Test validation fails with invalid side."""
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 100000,
            "side": "invalid",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })


def test_limit_order_trade_payload_validate_negative_limit_price():
    """Test validation fails with negative limit price."""
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 100000,
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": -1.3
        })


def test_limit_order_trade_payload_validate_zero_limit_price():
    """Test validation passes with zero limit price."""
    json_dict = {
        "symbol": "EURUSD",
        "asset_type": "FxSpot",
        "quantity": 100000,
        "side": "long",
        "sl_tp": {
            "stop_loss": {"type": "pip", "price": 1.5},
            "take_profit": {"type": "pip", "price": 2.5}
        },
        "limit_price": 0
    }
    
    payload = LimitOrderTradePayload.from_json(json_dict)
    
    assert payload.limit_price == 0


def test_limit_order_trade_payload_validate_invalid_asset_type():
    """Test validation fails with invalid asset type."""
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "InvalidAssetType",
            "quantity": 100000,
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3
        })


def test_limit_order_trade_payload_validate_additional_property():
    """Test validation fails with additional properties."""
    with pytest.raises(ValidationError):
        LimitOrderTradePayload.from_json({
            "symbol": "EURUSD",
            "asset_type": "FxSpot",
            "quantity": 100000,
            "side": "long",
            "sl_tp": {
                "stop_loss": {"type": "pip", "price": 1.5},
                "take_profit": {"type": "pip", "price": 2.5}
            },
            "limit_price": 1.3,
            "extra_field": "value"
        })
