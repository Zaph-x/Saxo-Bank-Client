import pytest
from datetime import datetime
from data_models.price.price_info import PriceInfo


def test_price_info_initialization():
    # Sample data as returned from the Saxo API
    sample_data = {
        "Quote": {
            "Bid": 100.5,
            "Mid": 101.0,
            "Ask": 101.5,
            "DelayedByMinutes": 0,
            "MarketState": "Open"
        },
        "LastUpdated": "2025-05-30T14:30:45.123Z",
        "AssetType": "Stock",
        "Uic": 123456,
        "DisplayAndFormat": {
            "Symbol": "AAPL",
            "OrderDecimals": 2,
            "Format": "Normal",
            "Currency": "USD"
        }
    }
    
    # Initialize the PriceInfo object
    price_info = PriceInfo(sample_data)
    
    # Assert all attributes are correctly initialized
    assert price_info.bid == 100.5
    assert price_info.mid == 101.0
    assert price_info.ask == 101.5
    assert price_info.delayed_by == 0
    assert price_info.market_state == "Open"
    assert price_info.asset_type == "Stock"
    assert price_info.uic == 123456
    assert price_info.symbol == "AAPL"
    assert price_info.order_decimals == 2
    assert price_info.allow_decimal_pips is False
    assert price_info.currency == "USD"
    assert isinstance(price_info.last_update, datetime)
    assert price_info.last_update.year == 2025
    assert price_info.last_update.month == 5
    assert price_info.last_update.day == 30


def test_get_decimal_size():
    # Test with normal format
    normal_data = {
        "Quote": {
            "Bid": 100.0,
            "Mid": 101.0, 
            "Ask": 102.0,
            "DelayedByMinutes": 0,
            "MarketState": "Open"
        },
        "LastUpdated": "2025-05-30T12:00:00.000Z",
        "AssetType": "Stock",
        "Uic": 1234,
        "DisplayAndFormat": {
            "Symbol": "TEST",
            "OrderDecimals": 2,
            "Format": "Normal",
            "Currency": "USD"
        }
    }
    normal_price = PriceInfo(normal_data)
    assert normal_price.get_decimal_size() == 2
    
    # Test with decimal pips format
    decimal_pips_data = {
        "Quote": {
            "Bid": 100.0,
            "Mid": 101.0, 
            "Ask": 102.0,
            "DelayedByMinutes": 0,
            "MarketState": "Open"
        },
        "LastUpdated": "2025-05-30T12:00:00.000Z",
        "AssetType": "FxSpot",
        "Uic": 5678,
        "DisplayAndFormat": {
            "Symbol": "EURUSD",
            "OrderDecimals": 4,
            "Format": "AllowDecimalPips",
            "Currency": "USD"
        }
    }
    decimal_pips_price = PriceInfo(decimal_pips_data)
    assert decimal_pips_price.get_decimal_size() == 5


def test_to_json():
    # Sample data
    sample_data = {
        "Quote": {
            "Bid": 150.75,
            "Mid": 151.25,
            "Ask": 151.75,
            "DelayedByMinutes": 0,
            "MarketState": "Open"
        },
        "LastUpdated": "2025-05-30T15:45:30.500Z",
        "AssetType": "Stock",
        "Uic": 987654,
        "DisplayAndFormat": {
            "Symbol": "MSFT",
            "OrderDecimals": 2,
            "Format": "Normal",
            "Currency": "USD"
        }
    }
    
    # Initialize the PriceInfo object
    price_info = PriceInfo(sample_data)
    
    # Get the JSON representation
    json_data = price_info.to_json()
    
    # Verify JSON data
    assert json_data["bid"] == 150.75
    assert json_data["mid"] == 151.25
    assert json_data["ask"] == 151.75
    assert json_data["delayed_by_minutes"] == 0
    assert json_data["market_state"] == "Open"
    assert json_data["asset_type"] == "Stock"
    assert json_data["uic"] == 987654
    assert json_data["symbol"] == "MSFT"
    assert json_data["order_decimals"] == 2
    assert json_data["allow_decimal_pips"] is False
    assert json_data["currency"] == "USD"
    assert "last_update" in json_data
    # Check that last_update is a valid ISO formatted string
    assert "2025-05-30T15:45:30.500" in json_data["last_update"]
