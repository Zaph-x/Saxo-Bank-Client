import pytest
from data_models.balance_information import BalanceInformation


def test_balance_information_init():
    """Test initialization with complete data."""
    data = {
        "CashBalance": 1000.5,
        "Currency": "USD",
        "TotalValue": 2000.25,
        "MarginAvailableForTrading": 800.75,
        "NetPositionsCount": 5,
        "OrdersCount": 3,
    }
    
    balance_info = BalanceInformation(data)
    
    assert balance_info.cash_balance == 1000.5
    assert balance_info.Currency == "USD"
    assert balance_info.total_value == 2000.25
    assert balance_info.margin_available == 800.75
    assert balance_info.net_positions_count == 5
    assert balance_info.orders_count == 3
    assert balance_info._data == data


def test_balance_information_init_with_missing_data():
    """Test initialization with missing data defaults to expected values."""
    data = {
        "CashBalance": 1000.5,
        "Currency": "USD",
    }
    
    balance_info = BalanceInformation(data)
    
    assert balance_info.cash_balance == 1000.5
    assert balance_info.Currency == "USD"
    assert balance_info.total_value == 0
    assert balance_info.margin_available == 0
    assert balance_info.net_positions_count == 0
    assert balance_info.orders_count == 0


def test_balance_information_init_with_empty_data():
    """Test initialization with empty data defaults to expected values."""
    data = {}
    
    balance_info = BalanceInformation(data)
    
    assert balance_info.cash_balance == 0
    assert balance_info.Currency == ""
    assert balance_info.total_value == 0
    assert balance_info.margin_available == 0
    assert balance_info.net_positions_count == 0
    assert balance_info.orders_count == 0


def test_balance_information_to_json():
    """Test to_json method returns correct dictionary."""
    data = {
        "CashBalance": 1000.5,
        "Currency": "USD",
        "TotalValue": 2000.25,
        "MarginAvailableForTrading": 800.75,
        "NetPositionsCount": 5,
        "OrdersCount": 3,
    }
    
    balance_info = BalanceInformation(data)
    json_result = balance_info.to_json()
    
    assert json_result == {
        "CashBalance": 1000.5,
        "Currency": "USD",
        "TotalValue": 2000.25,
        "MarginAvailableForTrading": 800.75,
        "NetPositionsCount": 5,
        "OrdersCount": 3,
    }


def test_balance_information_to_json_with_modified_values():
    """Test to_json method returns values from object attributes, not original data."""
    data = {
        "CashBalance": 1000.5,
        "Currency": "USD",
        "TotalValue": 2000.25,
        "MarginAvailableForTrading": 800.75,
        "NetPositionsCount": 5,
        "OrdersCount": 3,
    }
    
    balance_info = BalanceInformation(data)
    # Modify some attributes
    balance_info.cash_balance = 1500.75
    balance_info.Currency = "EUR"
    
    json_result = balance_info.to_json()
    
    assert json_result == {
        "CashBalance": 1500.75,
        "Currency": "EUR",
        "TotalValue": 2000.25,
        "MarginAvailableForTrading": 800.75,
        "NetPositionsCount": 5,
        "OrdersCount": 3,
    }


def test_balance_information_get_property_existing():
    """Test get_property returns correct value for existing property."""
    data = {
        "CashBalance": 1000.5,
        "Currency": "USD",
        "CustomProperty": "custom_value",
    }
    
    balance_info = BalanceInformation(data)
    
    assert balance_info.get_property("CashBalance") == 1000.5
    assert balance_info.get_property("Currency") == "USD"
    assert balance_info.get_property("CustomProperty") == "custom_value"


def test_balance_information_get_property_nonexistent():
    """Test get_property returns None for non-existent property."""
    data = {
        "CashBalance": 1000.5,
    }
    
    balance_info = BalanceInformation(data)
    
    assert balance_info.get_property("NonExistentProperty") is None
