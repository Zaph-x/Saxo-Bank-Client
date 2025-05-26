import pytest
import json
from jsonschema.exceptions import ValidationError
from data_models.trading.take_profit import TakeProfit
from data_models.price.price_type import PriceType


def test_take_profit_init_with_string_type():
    """Test initialization with string type parameter."""
    take_profit = TakeProfit(type="pip", price=1.5)
    assert take_profit.type == PriceType.PIP
    assert take_profit.price == 1.5


def test_take_profit_init_with_enum_type():
    """Test initialization with PriceType enum parameter."""
    take_profit = TakeProfit(type=PriceType.PERCENT, price=2.0)
    assert take_profit.type == PriceType.PERCENT
    assert take_profit.price == 2.0


def test_take_profit_to_json():
    """Test serializing TakeProfit to JSON."""
    take_profit = TakeProfit(type=PriceType.PIP, price=1.5)
    json_str = take_profit.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["type"] == "pip"
    assert json_dict["price"] == 1.5


def test_take_profit_from_json_with_string():
    """Test deserializing TakeProfit from JSON string."""
    json_str = """{"type":"pip","price":1.5}"""
    take_profit = TakeProfit.from_json(json_str)
    
    assert take_profit.type == PriceType.PIP
    assert take_profit.price == 1.5


def test_take_profit_from_json_with_dict():
    """Test deserializing TakeProfit from dict."""
    json_dict = {"type": "percent", "price": 2.0}
    take_profit = TakeProfit.from_json(json_dict)
    
    assert take_profit.type == PriceType.PERCENT
    assert take_profit.price == 2.0


def test_take_profit_validation_invalid_type():
    """Test validation fails with invalid price type."""
    with pytest.raises(ValidationError):
        TakeProfit.from_json({"type": "invalid_type", "price": 1.5})


def test_take_profit_validation_negative_price():
    """Test validation fails with negative price."""
    with pytest.raises(ValidationError):
        TakeProfit.from_json({"type": "pip", "price": -1.5})


def test_take_profit_validation_missing_price():
    """Test validation fails with missing price."""
    with pytest.raises(ValidationError):
        TakeProfit.from_json({"type": "pip"})


def test_take_profit_validation_missing_type():
    """Test validation fails with missing type."""
    with pytest.raises(ValidationError):
        TakeProfit.from_json({"price": 1.5})


def test_take_profit_validation_additional_property():
    """Test validation fails with additional property."""
    with pytest.raises(ValidationError):
        TakeProfit.from_json({"type": "pip", "price": 1.5, "extra": "field"})


def test_take_profit_calculate_price_percent():
    """Test calculate_price with PERCENT type."""
    take_profit = TakeProfit(type=PriceType.PERCENT, price=50)
    assert take_profit.calculate_price() == 0.5


def test_take_profit_calculate_price_price():
    """Test calculate_price with PRICE type."""
    take_profit = TakeProfit(type=PriceType.PRICE, price=1.5)
    assert take_profit.calculate_price() == 1.5


def test_take_profit_calculate_price_pip():
    """Test calculate_price with PIP type raises NotImplementedError."""
    take_profit = TakeProfit(type=PriceType.PIP, price=1.5)
    with pytest.raises(NotImplementedError, match="PIP calculation is not implemented."):
        take_profit.calculate_price()


def test_take_profit_calculate_price_invalid_type():
    """Test calculate_price with invalid type raises ValueError."""
    # This test works by monkey-patching the type attribute
    take_profit = TakeProfit(type=PriceType.PIP, price=1.5)
    take_profit.type = "invalid_type"
    with pytest.raises(ValueError, match="Invalid price type:"):
        take_profit.calculate_price()
