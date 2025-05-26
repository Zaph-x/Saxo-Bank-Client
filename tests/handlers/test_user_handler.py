import pytest
from unittest.mock import Mock, patch
from requests import Session, Response
from handlers.user_handler import UserHandler
from data_models.response_models import UserModel


class TestUserHandler:
    @pytest.fixture
    def mock_session(self):
        """Create a mock session with authorization headers."""
        session = Mock(spec=Session)
        session.headers = {"Authorization": "Bearer token123"}
        return session
    
    @pytest.fixture
    def user_handler(self, mock_session):
        """Create a UserHandler instance with a mock session."""
        base_url = "https://api.example.com"
        return UserHandler(mock_session, base_url)

    def test_get_user(self, user_handler, mock_session):
        """Test getting user information."""
        # Set up the mock response for the session get method
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "AssociatedAccountGroupOperations": [],
            "AssociatedAccountOperations": [],
            "AssociatedClientOperations": [],
            "AssociatedUserOperations": [],
            "ClientId": 12345,
            "ElevatedOperations": [],
            "GeneralOperations": [],
            "LinkedOperations": [],
            "UserId": 67890
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        user = user_handler.get_user()
        
        # Verify the get request was made with the correct URL
        mock_session.get.assert_called_once_with("https://api.example.com/root/v2/user")
        
        # Verify the response was properly processed
        assert isinstance(user, UserModel)
        assert user.client_id == 12345
        assert user.user_id == 67890

    def test_get_client_info(self, user_handler, mock_session):
        """Test getting client information."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        user_handler._get_client_info()
        
        # Verify the get request was made with the correct URL
        mock_session.get.assert_called_once_with("https://api.example.com/port/v1/clients/me")
        
        # Verify the client info was properly stored
        assert user_handler.client_info == {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
    
    def test_default_currency(self, user_handler):
        """Test getting the default currency."""
        # Set the client info directly
        user_handler.client_info = {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
        
        assert user_handler.default_currency == "USD"
    
    def test_default_account_key(self, user_handler):
        """Test getting the default account key."""
        # Set the client info directly
        user_handler.client_info = {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
        
        assert user_handler.default_account_key == "account123"
    
    def test_client_key(self, user_handler):
        """Test getting the client key."""
        # Set the client info directly
        user_handler.client_info = {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
        
        assert user_handler.client_key == "client456"
    
    def test_legal_assets(self, user_handler):
        """Test getting legal asset types."""
        # Set the client info directly
        user_handler.client_info = {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
        
        assert user_handler.legal_assets == ["FxSpot", "Stock"]
    
    def test_properties_trigger_get_client_info(self, user_handler, mock_session):
        """Test that accessing properties triggers a client info fetch if not already loaded."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "DefaultCurrency": "USD",
            "DefaultAccountKey": "account123",
            "ClientKey": "client456",
            "LegalAssetTypes": ["FxSpot", "Stock"]
        }
        mock_session.get.return_value = mock_response
        
        # Access a property without setting client_info first
        assert user_handler.default_currency == "USD"
        
        # Verify the get request was made
        mock_session.get.assert_called_once_with("https://api.example.com/port/v1/clients/me")
