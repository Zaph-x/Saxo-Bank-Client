import pytest
import json
from jsonschema.exceptions import ValidationError
from data_models.trading.stop_loss import StopLoss
from data_models.price.price_type import PriceType


def test_stop_loss_init_with_string_type():
    """Test initialization with string type parameter."""
    stop_loss = StopLoss(type="pip", price=1.5)
    assert stop_loss.type == PriceType.PIP
    assert stop_loss.price == 1.5


def test_stop_loss_init_with_enum_type():
    """Test initialization with PriceType enum parameter."""
    stop_loss = StopLoss(type=PriceType.PERCENT, price=2.0)
    assert stop_loss.type == PriceType.PERCENT
    assert stop_loss.price == 2.0


def test_stop_loss_to_json():
    """Test serializing StopLoss to JSON."""
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    json_str = stop_loss.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["type"] == "pip"
    assert json_dict["price"] == 1.5


def test_stop_loss_from_json_with_string():
    """Test deserializing StopLoss from JSON string."""
    json_str = """{"type":"pip","price":1.5}"""
    stop_loss = StopLoss.from_json(json_str)
    
    assert stop_loss.type == PriceType.PIP
    assert stop_loss.price == 1.5


def test_stop_loss_from_json_with_dict():
    """Test deserializing StopLoss from dict."""
    json_dict = {"type": "percent", "price": 2.0}
    stop_loss = StopLoss.from_json(json_dict)
    
    assert stop_loss.type == PriceType.PERCENT
    assert stop_loss.price == 2.0


def test_stop_loss_validation_invalid_type():
    """Test validation fails with invalid price type."""
    with pytest.raises(ValidationError):
        StopLoss.from_json({"type": "invalid_type", "price": 1.5})


def test_stop_loss_validation_negative_price():
    """Test validation fails with negative price."""
    with pytest.raises(ValidationError):
        StopLoss.from_json({"type": "pip", "price": -1.5})


def test_stop_loss_validation_missing_price():
    """Test validation fails with missing price."""
    with pytest.raises(ValidationError):
        StopLoss.from_json({"type": "pip"})


def test_stop_loss_validation_missing_type():
    """Test validation fails with missing type."""
    with pytest.raises(ValidationError):
        StopLoss.from_json({"price": 1.5})


def test_stop_loss_validation_additional_property():
    """Test validation fails with additional property."""
    with pytest.raises(ValidationError):
        StopLoss.from_json({"type": "pip", "price": 1.5, "extra": "field"})


def test_stop_loss_calculate_price_percent():
    """Test calculate_price with PERCENT type."""
    stop_loss = StopLoss(type=PriceType.PERCENT, price=50)
    assert stop_loss.calculate_price() == 0.5


def test_stop_loss_calculate_price_price():
    """Test calculate_price with PRICE type."""
    stop_loss = StopLoss(type=PriceType.PRICE, price=1.5)
    assert stop_loss.calculate_price() == 1.5


def test_stop_loss_calculate_price_pip():
    """Test calculate_price with PIP type raises NotImplementedError."""
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    with pytest.raises(NotImplementedError, match="PIP calculation is not implemented."):
        stop_loss.calculate_price()


def test_stop_loss_calculate_price_invalid_type():
    """Test calculate_price with invalid type raises ValueError."""
    # This test works by monkey-patching the type attribute
    stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
    stop_loss.type = "invalid_type"
    with pytest.raises(ValueError, match="Invalid price type:"):
        stop_loss.calculate_price()


def test_stop_loss_validate_price_not_number():
    """Test _validate with non-number price raises ValueError."""
    with pytest.raises(ValueError, match="Invalid price. Must be a number."):
        stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
        stop_loss.price = "not_a_number"
        stop_loss._validate()


def test_stop_loss_validate_invalid_type():
    """Test _validate with invalid type raises ValueError."""
    with pytest.raises(ValueError, match="Invalid price type:"):
        stop_loss = StopLoss(type=PriceType.PIP, price=1.5)
        stop_loss.type = "invalid_type"
        stop_loss._validate()
