import pytest
import json
from jsonschema.exceptions import ValidationError
from data_models.saxo.place_related_or_oco_order import PlaceRelatedOrOcoOrderModel


def test_place_related_or_oco_order_model_init():
    """Test initialization with all required parameters."""
    model = PlaceRelatedOrOcoOrderModel(
        AccountKey="12345",
        Amount=100000,
        AssetType="FxSpot",
        BuySell="Buy",
        OrderType="Limit",
        OrderPrice=1.3,
        Uic=21,
        OrderDuration={"OrderDurationType": "DayOrder"},
        AmountType="Quantity"
    )
    
    assert model.AccountKey == "12345"
    assert model.Amount == 100000
    assert model.AssetType == "FxSpot"
    assert model.BuySell == "Buy"
    assert model.OrderType == "Limit"
    assert model.OrderPrice == 1.3
    assert model.Uic == 21
    assert model.OrderDuration == {"OrderDurationType": "DayOrder"}
    assert model.AmountType == "Quantity"


def test_place_related_or_oco_order_model_init_with_defaults():
    """Test initialization with defaults."""
    model = PlaceRelatedOrOcoOrderModel(
        AccountKey="12345",
        Amount=100000,
        AssetType="FxSpot",
        BuySell="Buy",
        OrderType="Limit",
        OrderPrice=1.3,
        Uic=21
    )
    
    assert model.AccountKey == "12345"
    assert model.Amount == 100000
    assert model.AssetType == "FxSpot"
    assert model.BuySell == "Buy"
    assert model.OrderType == "Limit"
    assert model.OrderPrice == 1.3
    assert model.Uic == 21
    assert model.OrderDuration is None
    assert model.AmountType == "Quantity"


def test_place_related_or_oco_order_model_to_json():
    """Test serializing to JSON."""
    model = PlaceRelatedOrOcoOrderModel(
        AccountKey="12345",
        Amount=100000,
        AssetType="FxSpot",
        BuySell="Buy",
        OrderType="Limit",
        OrderPrice=1.3,
        Uic=21,
        OrderDuration={"OrderDurationType": "DayOrder"},
        AmountType="Quantity"
    )
    
    json_str = model.to_json()
    json_dict = json.loads(json_str)
    
    assert json_dict["accountKey"] == "12345"
    assert json_dict["amount"] == 100000
    assert json_dict["assetType"] == "FxSpot"
    assert json_dict["buySell"] == "Buy"
    assert json_dict["orderType"] == "Limit"
    assert json_dict["orderPrice"] == 1.3
    assert json_dict["uic"] == 21
    assert json_dict["orderDuration"] == {"orderDurationType": "DayOrder"}
    assert json_dict["amountType"] == "Quantity"


def test_place_related_or_oco_order_model_from_json_with_dict():
    """Test deserializing from JSON dict."""
    json_dict = {
        "AccountKey": "12345",
        "Amount": 100000,
        "AssetType": "FxSpot",
        "BuySell": "Buy",
        "OrderType": "Limit",
        "OrderPrice": 1.3,
        "Uic": 21,
        "OrderDuration": {"OrderDurationType": "DayOrder"},
        "AmountType": "Quantity"
    }
    
    model = PlaceRelatedOrOcoOrderModel.from_json(json_dict)
    
    assert model.AccountKey == "12345"
    assert model.Amount == 100000
    assert model.AssetType == "FxSpot"
    assert model.BuySell == "Buy"
    assert model.OrderType == "Limit"
    assert model.OrderPrice == 1.3
    assert model.Uic == 21
    assert model.OrderDuration == {"OrderDurationType": "DayOrder"}
    assert model.AmountType == "Quantity"


def test_place_related_or_oco_order_model_from_json_with_string():
    """Test deserializing from JSON string."""
    json_str = """
    {
        "AccountKey": "12345",
        "Amount": 100000,
        "AssetType": "FxSpot",
        "BuySell": "Buy",
        "OrderType": "Limit",
        "OrderPrice": 1.3,
        "Uic": 21,
        "OrderDuration": {"OrderDurationType": "DayOrder"},
        "AmountType": "Quantity"
    }
    """
    
    model = PlaceRelatedOrOcoOrderModel.from_json(json.loads(json_str))
    
    assert model.AccountKey == "12345"
    assert model.Amount == 100000
    assert model.AssetType == "FxSpot"
    assert model.BuySell == "Buy"
    assert model.OrderType == "Limit"
    assert model.OrderPrice == 1.3
    assert model.Uic == 21
    assert model.OrderDuration == {"OrderDurationType": "DayOrder"}
    assert model.AmountType == "Quantity"


def test_place_related_or_oco_order_model_validate_invalid_buy_sell():
    """Test validation with invalid BuySell value."""
    json_dict = {
        "AccountKey": "12345",
        "Amount": 100000,
        "AssetType": "FxSpot",
        "BuySell": "Invalid",
        "OrderType": "Limit",
        "OrderPrice": 1.3,
        "Uic": 21
    }
    
    with pytest.raises(ValidationError):
        PlaceRelatedOrOcoOrderModel.from_json(json_dict)


def test_place_related_or_oco_order_model_validate_invalid_amount_type():
    """Test validation with invalid AmountType value."""
    json_dict = {
        "AccountKey": "12345",
        "Amount": 100000,
        "AssetType": "FxSpot",
        "BuySell": "Buy",
        "OrderType": "Limit",
        "OrderPrice": 1.3,
        "Uic": 21,
        "AmountType": "Invalid"
    }
    
    with pytest.raises(ValidationError):
        PlaceRelatedOrOcoOrderModel.from_json(json_dict)
