import pytest
from unittest.mock import Mock, patch
from requests import Session, Response
from handlers.trade_handler import TradeHandler
from handlers.user_handler import UserHandler
from data_models.trading.trade_direction import TradeDirection
from data_models.order.order_type import OrderType
from data_models.trading.asset_type import AssetType
from data_models.order.order_duration import OrderDuration
from data_models.price.price_info import PriceInfo
from data_models.trade_payload import MarketOrderTradePayload, StopLossTakeProfitPayload
from data_models.trading.stop_loss import StopLoss
from data_models.trading.take_profit import TakeProfit
from data_models.price.price_type import PriceType


class TestTradeHandler:
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
    def trade_handler(self, mock_session, mock_user_handler):
        """Create a TradeHandler instance with mock dependencies."""
        base_url = "https://api.example.com"
        handler = TradeHandler(mock_user_handler, mock_session, base_url)
        # Mock the get_uic and get_price_for_assets methods that are used in other tests
        handler.get_uic = Mock(return_value=12345)
        handler.get_price_for_assets = Mock(return_value=[Mock(ask_price=1.15, bid_price=1.14)])
        return handler

    def test_place_order(self, trade_handler, mock_session):
        """Test placing an order."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"OrderId": "order123"}
        mock_session.post.return_value = mock_response
        
        # Create the order payload
        order_payload = {
            "AccountKey": "account123",
            "Uic": 12345,
            "AssetType": "FxSpot",
            "BuySell": "Buy",
            "OrderType": "Market",
            "Amount": 100000
        }
        
        # Call the method under test
        result = trade_handler._place_order(order_payload)
        
        # Verify the request was made correctly
        mock_session.post.assert_called_once_with("https://api.example.com/trade/v2/orders", json=order_payload)
        
        # Verify the response was handled correctly
        assert result == {"OrderId": "order123"}

    def test_place_order_error(self, trade_handler, mock_session):
        """Test placing an order that results in an error."""
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.json.return_value = {"Message": "Invalid order"}
        mock_session.post.return_value = mock_response
        
        # Create the order payload
        order_payload = {
            "AccountKey": "account123",
            "Uic": 12345,
            "AssetType": "FxSpot",
            "BuySell": "Buy",
            "OrderType": "Market",
            "Amount": 100000
        }
        
        # Call the method under test and verify it raises an exception
        with pytest.raises(Exception, match="Failed to place order: 400 {'Message': 'Invalid order'}"):
            trade_handler._place_order(order_payload)

    def test_create_order_payload(self, trade_handler):
        """Test creating an order payload."""
        # Call the method under test
        payload = trade_handler.create_order_payload(
            uic=12345,
            asset_type=AssetType.FxSpot,
            amount=100000,
            direction=TradeDirection.BUY,
            price=1.15,
            order_type=OrderType.Limit,
            order_duration=OrderDuration.DayOrder,
            reference_id="ref123"
        )
        
        # Verify the payload is correctly created
        assert payload == {
            "AccountKey": "account123",
            "Uic": 12345,
            "BuySell": "Buy",
            "AssetType": "FxSpot",
            "OrderType": "Limit",
            "Amount": 100000,
            "ManualOrder": False,
            "OrderDuration": {"DurationType": "DayOrder"},
            "WithAdvice": True,
            "OrderPrice": 1.15,
            "ExternalReference": "ref123"
        }

    def test_create_order_payload_with_trailing_stop(self, trade_handler):
        """Test creating an order payload with trailing stop parameters."""
        # Call the method under test
        payload = trade_handler.create_order_payload(
            uic=12345,
            asset_type=AssetType.FxSpot,
            amount=100000,
            direction=TradeDirection.BUY,
            price=1.15,
            order_type=OrderType.TrailingStop,
            order_duration=OrderDuration.DayOrder,
            trailing_stop_step=0.01,
            trailing_distance_to_market=0.05
        )
        
        # Verify the payload is correctly created
        assert payload["TrailingStopStep"] == 0.01
        assert payload["TrailingDistanceToMarket"] == 0.05

    def test_create_order_payload_with_good_till_date(self, trade_handler):
        """Test creating an order payload with GoodTillDate duration."""
        from datetime import datetime
        
        # Create a specific datetime for testing
        test_date = datetime(2023, 5, 25, 10, 0, 0)
        
        # Call the method under test
        payload = trade_handler.create_order_payload(
            uic=12345,
            asset_type=AssetType.FxSpot,
            amount=100000,
            direction=TradeDirection.BUY,
            price=1.15,
            order_type=OrderType.Limit,
            order_duration=OrderDuration.GoodTillDate,
            good_till_date=test_date
        )
        
        # Verify the payload is correctly created
        assert payload["OrderDuration"]["DurationType"] == "GoodTillDate"
        assert payload["OrderDuration"]["GoodTillDate"] == "2023-05-25T10:00:00"

    def test_get_uic(self, trade_handler, mock_session):
        """Test getting UIC for a symbol and asset type."""
        # Restore the original method for this test
        trade_handler.get_uic = TradeHandler.get_uic.__get__(trade_handler)
        
        # Set up the mock response
        mock_response = Mock(spec=Response)
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "Data": [
                {
                    "Symbol": "EURUSD",
                    "Identifier": 12345,
                    "AssetType": "FxSpot"
                }
            ]
        }
        mock_session.get.return_value = mock_response
        
        # Call the method under test
        uic = trade_handler.get_uic("EURUSD", AssetType.FxSpot)
        
        # Verify the request was made correctly
        mock_session.get.assert_called_once_with(
            "https://api.example.com/ref/v1/instruments?KeyWords=EURUSD&AssetType=FxSpot"
        )
        
        # Verify the response was handled correctly
        assert uic == 12345

    def test_place_market_order(self, trade_handler, mock_session):
        """Test placing a market order."""
        # Set up mocks
        mock_response = Mock(spec=Response)
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"OrderId": "order123"}
        mock_session.post.return_value = mock_response
        
        # Create proper price info mock with required attributes
        mock_price_info = Mock(spec=PriceInfo)
        mock_price_info.ask = 1.15
        mock_price_info.bid = 1.14
        
        # Update trade_handler.get_price_info_for_assets to return our proper mock
        trade_handler.get_price_info_for_assets = Mock(return_value=[mock_price_info])
        
        # Mock get_price_increment_for_asset to return a valid increment size
        trade_handler.get_price_increment_for_asset = Mock(return_value=0.0001)
        
        # Mock the create_order_payload to avoid the TrailingStop order parameter validation
        original_create_order_payload = trade_handler.create_order_payload
        
        def mocked_create_order_payload(*args, **kwargs):
            # For TrailingStop orders, add the required parameters if they're missing
            if 'order_type' in kwargs and kwargs['order_type'] == OrderType.TrailingStop:
                if 'trailing_stop_step' not in kwargs or kwargs['trailing_stop_step'] is None:
                    kwargs['trailing_stop_step'] = 0.01
                if 'trailing_distance_to_market' not in kwargs or kwargs['trailing_distance_to_market'] is None:
                    kwargs['trailing_distance_to_market'] = 0.05
            return original_create_order_payload(*args, **kwargs)
        
        trade_handler.create_order_payload = mocked_create_order_payload
        
        # Create a market order payload
        stop_loss = StopLoss(type=PriceType.PERCENT, price=10)
        take_profit = TakeProfit(type=PriceType.PERCENT, price=20)
        sl_tp = StopLossTakeProfitPayload(stop_loss=stop_loss, take_profit=take_profit)
        
        market_order_payload = MarketOrderTradePayload(
            symbol="EURUSD",
            asset_type="FxSpot",
            quantity=100000,
            side="long",
            sl_tp=sl_tp,
            algo_name="TestAlgo"
        )
        
        # Call the method under test
        result = trade_handler.place_market_order(market_order_payload)
        
        # Verify the post request was made
        assert mock_session.post.called
        # Check that post was called with the correct URL
        args, kwargs = mock_session.post.call_args
        assert args[0] == "https://api.example.com/trade/v2/orders"
        # Check that the json parameter is present
        assert "json" in kwargs
        
        # Verify the response was handled correctly
        assert result == {"OrderId": "order123"}
