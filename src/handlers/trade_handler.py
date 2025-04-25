from requests import Session
from handlers.handler_base import HandlerBase
from objects.trade_direction import TradeDirection
from objects.order_type import OrderType
from objects.asset_type import AssetType
from objects.order_information import OrderInformation
from handlers.user_handler import UserHandler
from typing import List

class TradeHandler(HandlerBase):
    def __init__(self, user_handler: UserHandler, session: Session, base_url: str) -> None:
        super().__init__(session, base_url)
        self.user_handler = user_handler

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
        url = f"{self.base_url}/trade/v2/orders"
        data = {
            "Uic": uic,
            "BuySell": trade_direction.value,
            "AssetType": asset_type.value,
            "Amount": amount,
            "OrderPrice": price,
            "OrderType": order_type.value,
            "ManualOrder": True,
            "Duration": {"DurationType": "DayOrder"},
            "AccountKey": self.user_handler.default_account_key,
        }
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

        url = f"{self.base_url}/trade/v2/orders/{','.join(order_ids)}?AccountKey={self.user_handler.default_account_key}"
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
