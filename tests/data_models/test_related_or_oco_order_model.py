import pytest
import json
from jsonschema.exceptions import ValidationError
from data_models.saxo.related_or_oco_order import RelatedOrOcoOrderModel


def test_related_or_oco_order_model_init():
    """Test initialization with order_id."""
    model = RelatedOrOcoOrderModel(order_id="123456")
    
    assert model.order_id == "123456"


def test_related_or_oco_order_model_to_json():
    """Test serializing to JSON."""
    model = RelatedOrOcoOrderModel(order_id="123456")
    
    json_str = model.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["orderId"] == "123456"


def test_related_or_oco_order_model_from_json_with_dict():
    """Test deserializing from JSON dict."""
    json_dict = {"OrderId": "123456"}
    
    model = RelatedOrOcoOrderModel.from_json(json_dict)
    
    assert model.order_id == "123456"


def test_related_or_oco_order_model_from_json_with_string():
    """Test deserializing from JSON string."""
    json_str = """{"OrderId":"123456"}"""
    
    model = RelatedOrOcoOrderModel.from_json(json.loads(json_str))
    
    assert model.order_id == "123456"


def test_related_or_oco_order_model_validate_missing_order_id():
    """Test validation fails with missing OrderId."""
    with pytest.raises(ValidationError):
        RelatedOrOcoOrderModel.from_json({})


def test_related_or_oco_order_model_validate_empty_order_id():
    """Test initialization with empty order_id."""
    model = RelatedOrOcoOrderModel(order_id="")
    assert model.order_id == ""
