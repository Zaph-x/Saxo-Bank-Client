import pytest
from unittest.mock import MagicMock, patch
from handlers.price_handler import PriceHandler
from handlers.user_handler import UserHandler
from data_models.trading.asset_type import AssetType
from data_models.price.price_info import PriceInfo
from requests import Session


@pytest.fixture
def mock_session():
    # Create a real Session object but with mocked methods
    session = Session()
    session.get = MagicMock()
    session.post = MagicMock()
    session.put = MagicMock()
    session.delete = MagicMock()
    session.headers["Authorization"] = "Bearer mock-token"
    return session


@pytest.fixture
def mock_user_handler():
    user_handler = MagicMock(spec=UserHandler)
    user_handler.default_account_key = "test_account_key"
    user_handler.client_key = "test_client_key"
    return user_handler


@pytest.fixture
def price_handler(mock_session, mock_user_handler):
    return PriceHandler(mock_user_handler, mock_session, "https://test-api.saxobank.com", "TF_TEST")


def test_get_uic_for_symbol_success(price_handler, mock_session):
    # Mock response for successful UIC lookup
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Data": [
            {
                "Identifier": 12345,
                "Symbol": "AAPL",
                "AssetType": "Stock"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    
    # Call the method
    uic = price_handler.get_uic_for_symbol("AAPL", AssetType.Stock)
    
    # Verify the result
    assert uic == 12345
    
    # Verify the mock was called with the expected URL
    expected_url = f"{price_handler.base_url}/ref/v1/instruments?KeyWords=AAPL&AssetType={AssetType.Stock.value}"
    mock_session.get.assert_called_once_with(expected_url)


def test_get_uic_for_symbol_multiple_results(price_handler, mock_session):
    # Mock response with multiple matches
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Data": [
            {
                "Identifier": 12345,
                "Symbol": "AAPL",
                "AssetType": "Stock"
            },
            {
                "Identifier": 67890,
                "Symbol": "AAPL.OTC",
                "AssetType": "Stock"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    
    # Call the method with exact match
    uic = price_handler.get_uic_for_symbol("AAPL", AssetType.Stock)
    
    # Verify it found the exact match
    assert uic == 12345


def test_get_uic_for_symbol_not_found(price_handler, mock_session):
    # Mock response with no data
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Data": []
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    
    # Call the method
    uic = price_handler.get_uic_for_symbol("NONEXISTENT", AssetType.Stock)
    
    # Verify it returns None
    assert uic is None


def test_get_uic_for_symbol_caching(price_handler, mock_session):
    # Mock response for successful UIC lookup
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Data": [
            {
                "Identifier": 12345,
                "Symbol": "AAPL"
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    
    # First call should hit the API
    uic1 = price_handler.get_uic_for_symbol("AAPL", AssetType.Stock)
    assert uic1 == 12345
    
    # Second call should use the cache
    uic2 = price_handler.get_uic_for_symbol("AAPL", AssetType.Stock)
    assert uic2 == 12345
    
    # Verify get was only called once
    assert mock_session.get.call_count == 1


def test_get_price_info_for_assets(price_handler, mock_session, mock_user_handler):
    # Mock response for price info
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Data": [
            {
                "Quote": {
                    "Bid": 150.75,
                    "Mid": 151.25,
                    "Ask": 151.75,
                    "DelayedByMinutes": 0,
                    "MarketState": "Open"
                },
                "LastUpdated": "2025-05-30T15:45:30.500Z",
                "AssetType": "Stock",
                "Uic": 12345,
                "DisplayAndFormat": {
                    "Symbol": "AAPL",
                    "OrderDecimals": 2,
                    "Format": "Normal",
                    "Currency": "USD"
                }
            }
        ]
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    
    # Call the method
    price_info_list = price_handler.get_price_info_for_assets([12345], AssetType.Stock)
    
    # Verify the result
    assert len(price_info_list) == 1
    assert isinstance(price_info_list[0], PriceInfo)
    assert price_info_list[0].symbol == "AAPL"
    assert price_info_list[0].bid == 150.75
    
    # Verify the mock was called with the expected URL containing the account key
    expected_url = (
        f"{price_handler.base_url}/trade/v1/infoprices/list"
        f"?AccountKey={mock_user_handler.default_account_key}"
        f"&Amount=1000&Uics=12345&AssetType={AssetType.Stock.value}"
        f"&FieldGroups=DisplayAndFormat,Quote"
    )
    mock_session.get.assert_called_once()
    assert mock_session.get.call_args[0][0] == expected_url


def test_get_price(price_handler):
    # Mock the methods that get_price depends on
    price_handler.get_uic_for_symbol = MagicMock(return_value=12345)
    
    # Create a mock price info
    mock_price_info = MagicMock(spec=PriceInfo)
    price_handler.get_price_info_for_assets = MagicMock(return_value=[mock_price_info])
    
    # Call the method
    price = price_handler.get_price("AAPL", AssetType.Stock)
    
    # Verify the result
    assert price == mock_price_info
    
    # Verify the component methods were called appropriately
    price_handler.get_uic_for_symbol.assert_called_once_with("AAPL", AssetType.Stock)
    price_handler.get_price_info_for_assets.assert_called_once_with([12345], AssetType.Stock)


def test_get_price_with_no_uic(price_handler):
    # Mock get_uic_for_symbol to return None
    price_handler.get_uic_for_symbol = MagicMock(return_value=None)
    
    # Mock get_price_info_for_assets (shouldn't be called)
    price_handler.get_price_info_for_assets = MagicMock()
    
    # Call the method
    price = price_handler.get_price("NONEXISTENT", AssetType.Stock)
    
    # Verify the result
    assert price is None
    
    # Verify get_price_info_for_assets was not called
    price_handler.get_price_info_for_assets.assert_not_called()


def test_get_price_increment_for_asset(price_handler, mock_session, mock_user_handler):
    # Mock response for price increment
    mock_response = MagicMock()
    mock_response.json.return_value = {
            "TickSizeScheme": {'Elements': [{'HighPrice': 100000, 'TickSize': 0.01}]}
    }
    mock_response.raise_for_status = MagicMock()
    mock_session.get.return_value = mock_response
    
    # Call the method
    increment = price_handler.get_price_increment_for_asset(12345, AssetType.Stock)
    
    # Verify the result
    assert increment == [{'HighPrice': 100000, 'TickSize': 0.01}]
    
    # Verify the mock was called with the expected URL
    expected_url = (
        f"{price_handler.base_url}/ref/v1/instruments/details/12345/{AssetType.Stock.value}"
        f"?AccountKey={mock_user_handler.default_account_key}"
        f"&ClientKey={mock_user_handler.client_key}"
    )
    mock_session.get.assert_called_once()
    assert mock_session.get.call_args[0][0] == expected_url
