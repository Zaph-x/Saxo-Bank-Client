from requests import Session
from handlers.handler_base import HandlerBase
from data_models.trading.trade_direction import TradeDirection
from data_models.order.order_type import OrderType
from data_models.trading.asset_type import AssetType
from data_models.order.order_information import OrderInformation
from data_models.order.order_duration import OrderDuration
from data_models.price.price_info import PriceInfo
from handlers.user_handler import UserHandler
from typing import List
from datetime import datetime
from logging import Logger
from data_models.trade_payload import MarketOrderTradePayload
from typing import Optional
from utils.price import calculate_stop_loss, calculate_take_profit

logger = Logger(__name__)


class TradeHandler(HandlerBase):
    def __init__(self, user_handler: UserHandler, session: Session, base_url: str) -> None:
        super().__init__(session, base_url)
        self.user_handler = user_handler

    def _place_order(self, order_payload: dict) -> dict:
        """
        Places an order with the given payload.

        Args:
            order_payload (dict): The payload for the order.

        Returns:
            dict: The response from the API.
        """
        url = f"{self.base_url}/trade/v2/orders"
        response = self.session.post(url, json=order_payload)
        logger.debug(f"Placing order with payload: {order_payload}")
        logger.debug(f"Response status code: {response.status_code}")
        if not response.ok:
            raise Exception(f"Failed to place order: {response.status_code} {response.json()}")
        if response.ok:
            logger.debug(f"Order placed successfully: {response.json()}")
        return response.json()

    def place_market_order(
        self,
        market_order_payload: MarketOrderTradePayload,
    ) -> dict:
        """
        Places a market order with the given parameters.

        Args:
            market_order_payload (MarketOrderTradePayload): The payload for the market order.

        Returns:
            dict: The response from the API.
        """

        logger.debug("Getting UIC for the market order.")
        uic = self.get_uic(
            symbol=market_order_payload.symbol,
            asset_type=AssetType(market_order_payload.asset_type),
        )
        logger.debug(f"UIC for {market_order_payload.symbol} is {uic}.")
        logger.debug("Retrieving price information for the asset.")
        price_info = self.get_price_for_assets([uic], AssetType(market_order_payload.asset_type))[0]
        logger.debug(f"Price information for {market_order_payload.symbol}: {price_info}")

        logger.debug("Creating order payload for the market order.")
        stop_loss_order_payload = self.create_order_payload(
            uic=uic,
            asset_type=AssetType(market_order_payload.asset_type),
            amount=market_order_payload.quantity,
            order_type=OrderType.TrailingStop if market_order_payload.sl_tp.stop_loss.is_trailing else OrderType.Stop,
            direction=TradeDirection.SELL,
            price=calculate_stop_loss(price_info, market_order_payload),
            order_duration=OrderDuration.GoodTillCancel,
            reference_id=market_order_payload.algo_name if market_order_payload.algo_name else "",
        )
        take_profit_order_payload = self.create_order_payload(
            uic=uic,
            asset_type=AssetType(market_order_payload.asset_type),
            amount=market_order_payload.quantity,
            order_type=OrderType.Limit,
            direction=TradeDirection.SELL,
            price=calculate_take_profit(price_info, market_order_payload),
            order_duration=OrderDuration.GoodTillCancel,
            reference_id=market_order_payload.algo_name if market_order_payload.algo_name else "",
        )
        order_payload = self.create_order_payload(
            uic=uic,
            asset_type=AssetType(market_order_payload.asset_type),
            amount=market_order_payload.quantity,
            order_type=OrderType.Market,
            direction=TradeDirection.BUY,
            related_orders=[
                stop_loss_order_payload,
                take_profit_order_payload,
            ],
            order_duration=OrderDuration.DayOrder,
            reference_id=market_order_payload.algo_name if market_order_payload.algo_name else "",
        )
        logger.debug(f"Order payload created: {order_payload}")

        logger.info(f"Placing market order for {market_order_payload.quantity} units of {uic} at market price.")
        return self._place_order(order_payload)

    def _get_order_duration(
        self,
        order_duration: OrderDuration,
        default,
    ) -> dict:
        """
        Get the order duration based on the provided order duration type.

        Args:
            order_duration (OrderDuration): The order duration type.
            default: The default value to return if the order duration is not found.

        Returns:
            dict: The order duration.
        """

        switcher = {
            OrderDuration.DayOrder: {
                "DurationType": "DayOrder",
            },
            OrderDuration.GoodTillCancel: {
                "DurationType": "GoodTillCancel",
            },
            OrderDuration.GoodTillDate: {
                "DurationType": "GoodTillDate",
                "GoodTillDate": None,
            },
            OrderDuration.SessionClose: {
                "DurationType": "AtTheClose",
            },
            OrderDuration.SessionOpen: {
                "DurationType": "AtTheOpening",
            },
            OrderDuration.FillOrKill: {
                "DurationType": "FillOrKill",
            },
            OrderDuration.ImmediateOrCancel: {
                "DurationType": "ImmediateOrCancel",
            },
            OrderDuration.GoodForPeriod: {
                "DurationType": "GoodForPeriod",
            },
        }
        return switcher.get(order_duration, default)

    def create_order_payload(
        self,
        uic,
        asset_type: AssetType,
        amount: int,
        direction: TradeDirection = TradeDirection.LONG,
        price: float = -1,
        order_type: OrderType = OrderType.Market,
        order_duration: OrderDuration = OrderDuration.DayOrder,
        related_orders: List[dict] | List[str] = [],
        good_till_date: Optional[datetime] = None,
        with_client_advice: bool = False,
        reference_id: str = "",
        trailing_stop_step: Optional[float] = None,
        trailing_distance_to_market: Optional[float] = None,
        reference_price_info: Optional[PriceInfo] = None,
    ) -> dict:
        """
        Creates a payload for the order.

        Args:
            uic (int): The UIC of the asset.
            asset_type (AssetType): The type of asset being traded.
            amount (int): The amount to trade.
            direction (TradeDirection): The direction of the trade (buy/sell).
            price (float): The price at which to trade.
            order_type (OrderType): The type of order (e.g., "Limit", "Market").
            order_duration (OrderDuration): The duration of the order.
            related_orders (List[dict] | List[str]): Related orders.

        Returns:
            dict: The payload for the order.
        """
        order = {
            "AccountKey": self.user_handler.default_account_key,
            "Uic": uic,
            "BuySell": direction.value,
            "AssetType": asset_type.value,
            "OrderType": order_type.value,
            "Amount": amount,
            "ManualOrder": False,
            "OrderDuration": self._get_order_duration(order_duration, {"DurationType": "DayOrder"}),
            "WithAdvice": with_client_advice,
        }
        if len(related_orders) > 0:
            order["Orders"] = related_orders
        if order_type != OrderType.Market:
            order["OrderPrice"] = price

        if order_type == OrderType.TrailingStop:
            if trailing_stop_step is None or trailing_distance_to_market is None:
                trailing_stop_step = 0.01  # Default step if not provided
                trailing_distance_to_market = 0.01  # Default distance if not provided
            order["TrailingStopStep"] = trailing_stop_step
            order["TrailingDistanceToMarket"] = trailing_distance_to_market
        if reference_id:
            order["ExternalReference"] = reference_id
        if order_duration == OrderDuration.GoodTillDate and not good_till_date:
            raise ValueError("good_till_date must be provided for GoodTillDate order duration.")
        if order_duration == OrderDuration.GoodTillDate and good_till_date:
            order["OrderDuration"]["GoodTillDate"] = good_till_date.strftime("%Y-%m-%dT%H:%M:%S")

        return order

    def get_uic(
        self,
        symbol: str,
        asset_type: AssetType,
    ) -> int:
        """
        Retrieves the UIC for a given symbol and asset type.

        Args:
            symbol (str): The symbol of the asset.
            asset_type (AssetType): The type of asset being traded.

        Returns:
            int: The UIC of the asset.
        """
        url = f"{self.base_url}/ref/v1/instruments?KeyWords={symbol}&AssetType={asset_type.value}"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        if not data.get("Data"):
            raise ValueError(f"No data found for symbol {symbol} and asset type {asset_type}.")
        if len(data["Data"]) > 1:
            itm = [itm for itm in data["Data"] if itm["Symbol"] == symbol]
            if len(itm) == 1:
                return itm[0]["Identifier"]
            else:
                logger.warning(f"Multiple UICs found for symbol {symbol} and asset type {asset_type}.")
                for itm in data["Data"]:
                    logger.warning(f"UIC: {itm['Uic']}, Symbol: {itm['Symbol']}")
                raise ValueError(f"Multiple UICs found for symbol {symbol} and asset type {asset_type}.")
        return data["Data"][0]["Identifier"]

    def get_price_for_assets(
        self,
        uic: List[int],
        asset_type: AssetType,
    ) -> List[PriceInfo]:
        """
        Retrieves the price for a given asset or a list of assets.

        Args:
            uic (List[int]): The UIC(s) of the asset(s).
            asset_type (AssetType): The type of asset being traded.

        Returns:
            List[PriceInfo]: The list of price information of the asset(s).
        """
        url = f"{self.base_url}/trade/v1/infoprices/list?AccountKey={self.user_handler.default_account_key}&Amount=1000&Uics={','.join(map(str, uic))}&AssetType={asset_type.value}&FieldGroups=DisplayAndFormat,Quote"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        if not data.get("Data"):
            raise ValueError(f"No data found for UIC {uic} and asset type {asset_type}.")
        return [PriceInfo(price) for price in data["Data"]]

    def buy_market_sl_tp(
        self,
        uic,
        asset_type: AssetType,
        amount: int,
        stop_loss: float,
        take_profit: float,
        order_type: OrderType,
        trade_direction: TradeDirection,
    ):
        """
        Places a market order with stop loss and take profit.

        Args:
            uic (int): The UIC of the asset.
            amount (int): The amount to trade.
            stop_loss (float): The stop loss price.
            take_profit (float): The take profit price.
            order_type (str): The type of order (e.g., "Limit", "Market").
            trade_direction (TradeDirection): The direction of the trade (buy/sell).
            asset_type (AssetType): The type of asset being traded.

        Returns:
            dict: The response from the API.
        """
        logger.info(
            f"Placing {order_type} order for {amount} units of {uic} with stop loss {stop_loss} and take profit {take_profit}."
        )
        url = f"{self.base_url}/trade/v2/orders"
        data = self.create_order_payload(
            uic=uic,
            asset_type=asset_type,
            amount=amount,
            direction=trade_direction,
            order_type=order_type,
            order_duration=OrderDuration.DayOrder,
            related_orders=[
                {
                    "OrderType": OrderType.Stop.value,
                    "Amount": amount,
                    "OrderPrice": stop_loss,
                },
                {
                    "OrderType": OrderType.Limit.value,
                    "Amount": amount,
                    "OrderPrice": take_profit,
                },
            ],
        )

        data["AccountKey"] = self.user_handler.default_account_key

        response = self.session.post(url, json=data)
        if not response.ok:
            raise Exception(f"Failed to place order: {response.status_code} {response.json()}")
        return response.json()

    def place_day_order(
        self,
        uic,
        asset_type: AssetType,
        amount: int,
        price: float,
        order_type: OrderType,
        trade_direction: TradeDirection,
    ):
        """
        Places an order with the given parameters.

        Args:
            uic (int): The UIC of the asset.
            amount (int): The amount to trade.
            price (float): The price at which to trade.
            order_type (str): The type of order (e.g., "Limit", "Market").
            trade_direction (TradeDirection): The direction of the trade (buy/sell).
            asset_type (AssetType): The type of asset being traded.

        Returns:
            dict: The response from the API.
        """
        logger.info(
            f"Placing {order_type} order for {amount} units of {uic} at {price} with direction {trade_direction}. No stop loss. No take profit."
        )
        url = f"{self.base_url}/trade/v2/orders"
        data = self.create_order_payload(
            uic=uic,
            asset_type=asset_type,
            amount=amount,
            price=price,
            order_type=order_type,
            direction=trade_direction,
            order_duration=OrderDuration.DayOrder,
            with_client_advice=True,
        )

        data["AccountKey"] = self.user_handler.default_account_key

        response = self.session.post(url, json=data)
        if not response.ok:
            raise Exception(f"Failed to place order: {response.status_code} {response.json()}")
        return response.json()

    def get_all_orders(self) -> List[OrderInformation]:
        """
        Retrieves the orders for the account.

        Returns:
            dict: The orders.
        """
        url = f"{self.base_url}/port/v1/orders/me?fieldGroups=DisplayAndFormat"
        response = self.session.get(url)
        response.raise_for_status()
        return [OrderInformation(order) for order in response.json().get("Data", [])]

    def cancel_order(self, order_ids: List[str]):
        """
        Cancels an order with the given order ID.

        Args:
            order_ids (List[str]): The IDs of the orders to cancel. Should be one or more.

        Returns:
            dict: The response from the API.
        """
        if not order_ids:
            raise ValueError("order_ids must contain at least one order ID.")
        if type(order_ids) is not list:
            raise TypeError("order_ids must be a list.")
        if len(order_ids) > 10:
            raise ValueError("order_ids must contain at most 10 order IDs.")

        url = (
            f"{self.base_url}/trade/v2/orders/{','.join(order_ids)}?AccountKey={self.user_handler.default_account_key}"
        )
        response = self.session.delete(url)
        if not response.ok:
            raise Exception(f"Failed to cancel order: {response.status_code} {response.json()}")
        return response.json()

    def cancel_all_orders(self):
        """
        Cancels all orders for the account.

        Returns:
            dict: The response from the API.
        """
        orders = self.get_all_orders()
        order_ids = [order.order_id for order in orders]
        if not order_ids:
            raise ValueError("No orders to cancel.")
        return self.cancel_order(order_ids)

    def cancell_all_orders_for_asset(
        self,
        uic: int,
        asset_type: AssetType,
    ):
        """
        Cancels all orders for the given asset.

        Args:
            uic (int): The UIC of the asset.
            asset_type (AssetType): The type of asset being traded.

        Returns:
            dict: The response from the API.
        """
        url = f"{self.base_url}/trade/v2/orders?AccountKey={self.user_handler.default_account_key}&Uic={uic}&AssetType={asset_type.value}"
        response = self.session.delete(url)
        if not response.ok:
            raise Exception(f"Failed to cancel all orders: {response.status_code} {response.json()}")
        return response.json()
