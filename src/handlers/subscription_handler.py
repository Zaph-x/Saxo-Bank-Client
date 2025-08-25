from handlers.price_handler import PriceHandler
from handlers.user_handler import UserHandler
from utils.database import Database
from data_models.trading.asset_type import AssetType
import logging
from typing import Optional, List, Dict, Union
from requests import Session
from handlers.handler_base import HandlerBase

logger = logging.getLogger(__name__)

class SubscriptionHandler(HandlerBase):
    def __init__(self, price_handler: PriceHandler, user_handler: UserHandler, base_url: str, session: Session):
        """
        Initializes the SubscriptionHandler with necessary handlers and session.

        Args:
            price_handler (PriceHandler): Handler for managing price data
            user_handler (UserHandler): Handler for user-related operations
            base_url (str): Base URL for the API
            session (Session): Requests session for making API calls
        """
        super().__init__(session, base_url)
        self.price_handler = price_handler
        self.user_handler = user_handler

    def _subscribe(self, uic: int, asset_type: AssetType, context_id: str, timeframe: int, algo_name: str) -> Optional[str]:
        url = (
            f"{self.base_url}/trade/v1/infoprices/subscriptions"
        )
        body = {
            "Arguments": {
                "Uics": str(uic),
                "AssetType": asset_type.value,
                "AccountKey": self.user_handler.default_account_key,
            },
            "RefreshRate": timeframe,
            "ReferenceId": "TF"+str(uic).replace(',', '_')+f"_{asset_type.value}",
            "ContextId": context_id,
            "Tag": algo_name,
        }
        try:
            response = self.session.post(url, json=body)
            response.raise_for_status()
            data = response.json()
            if "ReferenceId" not in data:
                logger.warning(f"No subscription ID returned for UIC {uic} and asset type {asset_type}.")
                return None
            return data["ReferenceId"]
        except Exception as e:
            logger.error(f"Error creating price subscription for UIC {uic}: {e}")
            return None
 
    def create_price_subscription(self, asset: str, asset_type: AssetType, context_id: str, timeframe: int, algo_name: str) -> Optional[str]:
        """
        Creates a price subscription for a given asset.

        Args:
            asset (str): The asset identifier (symbol or UIC)
            asset_type (AssetType): The type of asset being traded
            timeframe (int): The timeframe for the subscription in milliseconds

        Returns:
            Optional[str]: The subscription ID if successful, None otherwise
        """
        uic = self.price_handler.get_uic_for_symbol(asset, asset_type)
        if uic is None:
            logger.error(f"Cannot create subscription: Unknown asset {asset} of type {asset_type}.")
            return None
        ref_id = self._subscribe(uic, asset_type, context_id, timeframe, algo_name)
        with Database() as db:
            params = (context_id, ref_id, algo_name, uic, str(asset_type), timeframe)
            db.execute(
                """
                INSERT INTO subscriptions (context_id, reference_id, algo_name, uic, asset_type, timeframe)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                params
            )
            logger.info(f"Subscription created for UIC {uic} with ID {ref_id}.")
            
        return ref_id

    def get_price_subscriptions(self, context_id: str = "") -> List[Dict[str, Union[str, int]]]:
        """
        Retrieves all price subscriptions for the given context ID.

        Args:
            context_id (str, optional): The context ID to filter subscriptions. Defaults to None.

        Returns:
            List[Dict[str, Union[str, int]]]: A list of dictionaries containing subscription details
        """
        items = []
        with Database() as db: 
            if context_id:
                items = db.execute(
                    "SELECT * FROM subscriptions",
                    (context_id,)
                )
            else:
                items = db.execute("SELECT * FROM subscriptions")
        if not items:
            logger.info("No price subscriptions found.")
            return []
        subscriptions = []
        for item in items:
            subscription = {
                "context_id": item[1],
                "reference_id": item[2],
                "algo_name": item[3],
                "uic": item[4],
                "asset_type": item[5],
                "timeframe": item[6],
                "created_at": item[7].isoformat() if item[7] else None
            }
            subscriptions.append(subscription)
        logger.info(f"Retrieved {len(subscriptions)} price subscriptions for context ID {context_id}.")
        return subscriptions
            
    def remove_price_subscription(self, context_id: str, reference_id) -> bool:
        """
        Removes a price subscription by its ID.

        Args:
            subscription_id (str): The ID of the subscription to remove

        Returns:
            bool: True if the subscription was successfully removed, False otherwise
        """
        url = f"{self.base_url}/trade/v1/prices/subscriptions/{context_id}/{reference_id}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error removing price subscription {reference_id}: {e}")
            return False
            
        with Database() as db:
            db.execute(
                "DELETE FROM subscriptions WHERE reference_id = %s",
                (reference_id,)
            )
            logger.info(f"Subscription {reference_id} removed successfully.")
        return True

    def remove_active_price_subscriptions(self, context_id: str) -> bool:
        """
        Removes all active price subscriptions for a given context ID.

        Args:
            context_id (str): The context ID for which to remove active subscriptions

        Returns:
            bool: True if all active subscriptions were successfully removed, False otherwise
        """
        url = f"{self.base_url}/trade/v1/prices/subscriptions/active/{context_id}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error removing active price subscriptions for context {context_id}: {e}")
            return False
           
        return True

    def resubscribe_all_price_subscriptions(self, context_id: str) -> None:
        """
        Resubscribes to all price subscriptions for a given context ID.

        Args:
            context_id (str): The context ID for which to resubscribe subscriptions
        """
        subscriptions = self.get_price_subscriptions(context_id)
        if not subscriptions:
            logger.info(f"No subscriptions found for context {context_id} to resubscribe.")
            return
        for sub in subscriptions:
            self._subscribe(int(sub["uic"]), AssetType(sub["asset_type"]), context_id, int(sub["timeframe"]), str(sub["algo_name"]))
        logger.info(f"Resubscribed to all price subscriptions for context {context_id}.")


    def remove_all_price_subscriptions(self, context_id: str, tag: Optional[str] = None) -> bool:
        """
        Removes all price subscriptions for a given context ID.

        Args:
            context_id (str): The context ID for which to remove subscriptions

        Returns:
            bool: True if all subscriptions were successfully removed, False otherwise
        """
        url = f"{self.base_url}/trade/v1/prices/subscriptions/{context_id}"
        if tag:
            url += f"?Tag={tag}"
        try:
            response = self.session.delete(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Error removing all price subscriptions for context {context_id}: {e}")
            return False
            
        with Database() as db:
            query = "DELETE FROM subscriptions WHERE context_id = %s"
            params = (context_id,)
            if tag:
                query += " AND algo_name = %s"
                params = (context_id, tag)
            db.execute(
                query,
                params
            )
            logger.info(f"All subscriptions for context {context_id} removed successfully.")
        return True


