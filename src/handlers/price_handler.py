from requests import Session
from handlers.handler_base import HandlerBase
from data_models.trading.asset_type import AssetType
from data_models.price.price_info import PriceInfo
from handlers.user_handler import UserHandler
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PriceHandler(HandlerBase):
    """
    Handler for retrieving price information from the Saxo Bank API.
    """
    
    def __init__(self, user_handler: UserHandler, session: Session, base_url: str) -> None:
        """
        Initialize the PriceHandler.

        Args:
            user_handler (UserHandler): The user handler with authentication information
            session (Session): The requests session
            base_url (str): The base URL for the Saxo Bank API
        """
        super().__init__(session, base_url)
        self.user_handler = user_handler
        self.uic_cache: Dict[str, Dict[AssetType, int]] = {}  # Cache for symbol->UIC lookups

    def get_price(self, symbol: str, asset_type: AssetType = AssetType.Stock) -> Optional[PriceInfo]:
        """
        Get the current price info for a symbol.

        Args:
            symbol (str): The symbol or friendly name of the asset
            asset_type (AssetType, optional): The type of asset. Defaults to AssetType.Stock.

        Returns:
            Optional[PriceInfo]: The price information of the asset, or None if not found
        """
        try:
            uic = self.get_uic_for_symbol(symbol, asset_type)
            if uic is None:
                logger.warning(f"No UIC found for symbol: {symbol}, asset type: {asset_type}")
                return None
                
            price_info_list = self.get_price_info_for_assets([uic], asset_type)
            if not price_info_list:
                return None
            return price_info_list[0]
        except Exception as e:
            logger.error(f"Error getting price for {symbol}: {e}")
            return None

    def get_uic_for_symbol(self, symbol: str, asset_type: AssetType) -> Optional[int]:
        """
        Retrieves the UIC for a given symbol and asset type.
        Uses a cache to avoid repeated API calls for the same symbol.

        Args:
            symbol (str): The symbol of the asset
            asset_type (AssetType): The type of asset being traded

        Returns:
            Optional[int]: The UIC of the asset, or None if not found
        """
        # Check cache first
        if symbol in self.uic_cache and asset_type in self.uic_cache[symbol]:
            return self.uic_cache[symbol][asset_type]

        try:
            url = f"{self.base_url}/ref/v1/instruments?KeyWords={symbol}&AssetType={asset_type.value}"
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("Data"):
                logger.warning(f"No data found for symbol {symbol} and asset type {asset_type}.")
                return None
                
            if len(data["Data"]) > 1:
                # Try to find exact match
                items = [item for item in data["Data"] if item.get("Symbol") == symbol]
                if len(items) == 1:
                    uic = items[0]["Identifier"]
                else:
                    logger.warning(f"Multiple UICs found for symbol {symbol} and asset type {asset_type}.")
                    for item in data["Data"]:
                        logger.warning(f"UIC: {item.get('Uic')}, Symbol: {item.get('Symbol')}")
                    # Use the first one as default
                    uic = data["Data"][0]["Identifier"]
            else:
                uic = data["Data"][0]["Identifier"]
            
            # Update cache
            if symbol not in self.uic_cache:
                self.uic_cache[symbol] = {}
            self.uic_cache[symbol][asset_type] = uic
            
            return uic
            
        except Exception as e:
            logger.error(f"Error getting UIC for {symbol}: {e}")
            return None

    def get_price_info_for_assets(self, uics: List[int], asset_type: AssetType) -> List[PriceInfo]:
        """
        Retrieves the price information for given assets.

        Args:
            uics (List[int]): The UICs of the assets
            asset_type (AssetType): The type of assets being queried

        Returns:
            List[PriceInfo]: The list of price information for the assets
        """
        if not uics:
            return []
            
        try:
            url = (
                f"{self.base_url}/trade/v1/infoprices/list"
                f"?AccountKey={self.user_handler.default_account_key}"
                f"&Amount=1000"
                f"&Uics={','.join(map(str, uics))}"
                f"&AssetType={asset_type.value}"
                f"&FieldGroups=DisplayAndFormat,Quote"
            )
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if not data.get("Data"):
                logger.warning(f"No price data found for UICs {uics} and asset type {asset_type}.")
                return []
                
            return [PriceInfo(price) for price in data["Data"]]
            
        except Exception as e:
            logger.error(f"Error getting price info for UICs {uics}: {e}")
            return []

    def get_price_increment_for_asset(self, uic: int, asset_type: AssetType) -> Optional[float]:
        """
        Retrieves the price increment for a given asset.

        Args:
            uic (int): The UIC of the asset
            asset_type (AssetType): The type of asset being traded

        Returns:
            Optional[float]: The price increment of the asset, or None if not found
        """
        try:
            url = (
                f"{self.base_url}/ref/v1/instruments/details/{uic}/{asset_type.value}"
                f"?AccountKey={self.user_handler.default_account_key}"
                f"&ClientKey={self.user_handler.client_key}"
            )
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            if "IncrementSize" not in data:
                logger.warning(f"No increment size found for UIC {uic} and asset type {asset_type}.")
                return None
                
            return data["IncrementSize"]
            
        except Exception as e:
            logger.error(f"Error getting price increment for UIC {uic}: {e}")
            return None
