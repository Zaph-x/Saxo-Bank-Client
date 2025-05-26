import pytest
import json
from jsonschema.exceptions import ValidationError
from data_models.trade_payload import StopLossTakeProfitPayload
from data_models.trading.stop_loss import StopLoss
from data_models.trading.take_profit import TakeProfit
from data_models.price.price_type import PriceType


def test_stop_loss_take_profit_payload_init_with_objects():
    """Test initialization with StopLoss and TakeProfit objects."""
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    take_profit = TakeProfit(type=PriceType.PIP, price=2.5)
    
    payload = StopLossTakeProfitPayload(stop_loss=stop_loss, take_profit=take_profit)
    
    assert payload.stop_loss is stop_loss
    assert payload.take_profit is take_profit


def test_stop_loss_take_profit_payload_init_with_dicts():
    """Test initialization with dictionaries."""
    stop_loss_dict = {"type": "pip", "price": 1.5}
    take_profit_dict = {"type": "pip", "price": 2.5}
    
    payload = StopLossTakeProfitPayload(stop_loss=stop_loss_dict, take_profit=take_profit_dict)
    
    assert isinstance(payload.stop_loss, StopLoss)
    assert payload.stop_loss.type == PriceType.PIP
    assert payload.stop_loss.price == 1.5
    
    assert isinstance(payload.take_profit, TakeProfit)
    assert payload.take_profit.type == PriceType.PIP
    assert payload.take_profit.price == 2.5


def test_stop_loss_take_profit_payload_to_json():
    """Test serializing to JSON."""
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    take_profit = TakeProfit(type=PriceType.PIP, price=2.5)
    
    payload = StopLossTakeProfitPayload(stop_loss=stop_loss, take_profit=take_profit)
    
    json_str = payload.to_json()
    json_dict = json.loads(json_str)
    
    assert "stopLoss" in json_dict
    assert json_dict["stopLoss"]["type"] == "pip"
    assert json_dict["stopLoss"]["price"] == 1.5
    
    assert "takeProfit" in json_dict
    assert json_dict["takeProfit"]["type"] == "pip"
    assert json_dict["takeProfit"]["price"] == 2.5


def test_stop_loss_take_profit_payload_from_json_with_dict():
    """Test deserializing from JSON dict."""
    json_dict = {
        "stop_loss": {"type": "pip", "price": 1.5},
        "take_profit": {"type": "pip", "price": 2.5}
    }
    
    payload = StopLossTakeProfitPayload.from_json(json_dict)
    
    assert isinstance(payload.stop_loss, StopLoss)
    assert payload.stop_loss.type == PriceType.PIP
    assert payload.stop_loss.price == 1.5
    
    assert isinstance(payload.take_profit, TakeProfit)
    assert payload.take_profit.type == PriceType.PIP
    assert payload.take_profit.price == 2.5


def test_stop_loss_take_profit_payload_from_json_with_string():
    """Test deserializing from JSON string."""
    json_str = """
    {
        "stop_loss": {"type": "pip", "price": 1.5},
        "take_profit": {"type": "pip", "price": 2.5}
    }
    """
    
    payload = StopLossTakeProfitPayload.from_json(json.loads(json_str))
    
    assert isinstance(payload.stop_loss, StopLoss)
    assert payload.stop_loss.type == PriceType.PIP
    assert payload.stop_loss.price == 1.5
    
    assert isinstance(payload.take_profit, TakeProfit)
    assert payload.take_profit.type == PriceType.PIP
    assert payload.take_profit.price == 2.5


def test_stop_loss_take_profit_payload_validate_missing_stop_loss():
    """Test validation fails with missing stop_loss."""
    with pytest.raises(ValidationError):
        StopLossTakeProfitPayload.from_json({"take_profit": {"type": "pip", "price": 2.5}})


def test_stop_loss_take_profit_payload_validate_missing_take_profit():
    """Test validation fails with missing take_profit."""
    with pytest.raises(ValidationError):
        StopLossTakeProfitPayload.from_json({"stop_loss": {"type": "pip", "price": 1.5}})


def test_stop_loss_take_profit_payload_validate_additional_property():
    """Test validation fails with additional property."""
    with pytest.raises(ValidationError):
        StopLossTakeProfitPayload.from_json({
            "stop_loss": {"type": "pip", "price": 1.5},
            "take_profit": {"type": "pip", "price": 2.5},
            "extra_field": "value"
        })
