import pytest
from unittest.mock import Mock, patch
from requests import Session, Response
from handlers.account_handler import AccountHandler
from handlers.user_handler import UserHandler
from data_models.balance_information import BalanceInformation
from data_models.saxo.position import PositionModel


class TestAccountHandler:
    @pytest.fixture
    def mock_session(self):
        """Create a mock session with authorization headers."""
        session = Mock(spec=Session)
        session.headers = {"Authorization": "Bearer token123"}
        return session
    
    @pytest.fixture
    def mock_user_handler(self):
        """Create a mock UserHandler."""
        user_handler = Mock(spec=UserHandler)
        user_handler.default_account_key = "account123"
        user_handler.client_key = "client456"
        return user_handler
    
    @pytest.fixture
    def account_handler(self, mock_session, mock_user_handler):
        """Create an AccountHandler instance with mock dependencies."""
        base_url = "https://api.example.com"
        return AccountHandler(mock_session, base_url, mock_user_handler)

    def test_get_account_info(self, account_handler, mock_session):
        """Test getting account information."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "AccountId": "account123",
            "AccountKey": "account123",
            "AccountGroupKey": "group789",
            "AccountType": "Normal",
            "Currency": "USD"
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        account_info = account_handler.get_account_info()
        
        # Verify the request was made correctly
        mock_session.get.assert_called_once_with("https://api.example.com/port/v1/accounts/account123")
        
        # Verify the response was handled correctly
        assert account_info == {
            "AccountId": "account123",
            "AccountKey": "account123",
            "AccountGroupKey": "group789",
            "AccountType": "Normal",
            "Currency": "USD"
        }

    def test_get_account_balance(self, account_handler, mock_session):
        """Test getting account balance."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "CashBalance": 10000.0,
            "Currency": "USD",
            "TotalValue": 10000.0,
            "MarginAvailableForTrading": 8000.0,
            "NetPositionsCount": 0,
            "OrdersCount": 0
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        balance = account_handler.get_account_balance()
        
        # Verify the request was made correctly
        mock_session.get.assert_called_once_with(
            "https://api.example.com/port/v1/balances?AccountKey=account123&ClientKey=client456"
        )
        
        # Verify the response was handled correctly
        assert balance == 10000.0

    def test_get_account_balance_information(self, account_handler, mock_session):
        """Test getting detailed account balance information."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "CashBalance": 10000.0,
            "Currency": "USD",
            "TotalValue": 10000.0,
            "MarginAvailableForTrading": 8000.0,
            "NetPositionsCount": 0,
            "OrdersCount": 0
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        balance_info = account_handler.get_account_balance_information()
        
        # Verify the request was made correctly
        mock_session.get.assert_called_once_with(
            "https://api.example.com/port/v1/balances?AccountKey=account123&ClientKey=client456"
        )
        
        # Verify the response was handled correctly
        assert isinstance(balance_info, BalanceInformation)
        assert balance_info.cash_balance == 10000.0
        assert balance_info.Currency == "USD"
        assert balance_info.total_value == 10000.0
        assert balance_info.margin_available == 8000.0
        assert balance_info.net_positions_count == 0
        assert balance_info.orders_count == 0

    def test_get_account_positions(self, account_handler, mock_session):
        """Test getting account positions."""
        # Set up the mock response for the first request
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "Data": [
                {
                    "NetPositionId": "position1",
                    "PositionId": "position1",
                    "PositionBase": {
                        "Amount": 100,
                        "ExecutionTimeOpen": "2023-05-25T10:00:00Z",
                        "LockedByBackOffice": False,
                        "Uic": 12345,
                        "Status": "Open",
                        "IsMarketOpen": True,
                        "CanBeClosed": True,
                        "OpenPrice": 150.0
                    },
                    "PositionView": {
                        "Ask": 155.0,
                        "Bid": 154.0,
                        "CurrentPrice": 154.5,
                        "Exposure": 15450.0
                    }
                }
            ]
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        positions = account_handler.get_account_positions()
        
        # Verify the request was made correctly
        mock_session.get.assert_called_once_with(
            "https://api.example.com/port/v1/positions?AccountKey=account123&ClientKey=client456"
        )
        
        # Verify the response was handled correctly
        assert len(positions) == 1
        assert isinstance(positions[0], PositionModel)
        assert positions[0].net_position_id == "position1"
        assert positions[0].amount == 100
        assert positions[0].open_price == 150.0
        assert positions[0].position_view.ask_price == 155.0
        assert positions[0].position_view.bid_price == 154.0

    def test_get_account_positions_with_next_page(self, account_handler, mock_session):
        """Test getting account positions with pagination."""
        # Set up the mock responses
        first_response = Mock(spec=Response)
        first_response.raise_for_status.return_value = None
        first_response.json.return_value = {
            "Data": [
                {
                    "NetPositionId": "position1",
                    "PositionId": "position1",
                    "PositionBase": {
                        "Amount": 100,
                        "Uic": 12345
                    },
                    "PositionView": {}
                }
            ],
            "__next": "https://api.example.com/port/v1/positions/next-page"
        }
        
        second_response = Mock(spec=Response)
        second_response.raise_for_status.return_value = None
        second_response.json.return_value = {
            "Data": [
                {
                    "NetPositionId": "position2",
                    "PositionId": "position2",
                    "PositionBase": {
                        "Amount": 200,
                        "Uic": 67890
                    },
                    "PositionView": {}
                }
            ]
        }
        
        mock_session.get.side_effect = [first_response, second_response]
        
        # Call the method under test
        positions = account_handler.get_account_positions()
        
        # Verify the requests were made correctly
        assert mock_session.get.call_count == 2
        mock_session.get.assert_any_call(
            "https://api.example.com/port/v1/positions?AccountKey=account123&ClientKey=client456"
        )
        mock_session.get.assert_any_call("https://api.example.com/port/v1/positions/next-page")
        
        # Verify the response was handled correctly
        assert len(positions) == 2
        assert positions[0].net_position_id == "position1"
        assert positions[0].amount == 100
        assert positions[1].net_position_id == "position2"
        assert positions[1].amount == 200
