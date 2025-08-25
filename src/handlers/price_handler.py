from requests import Session
from handlers.handler_base import HandlerBase
from data_models.trading.asset_type import AssetType
from data_models.price.price_info import PriceInfo
from handlers.user_handler import UserHandler
from typing import List, Dict, Optional, Union
import logging
import functools
from utils.database import Database

logger = logging.getLogger(__name__)


class PriceHandler(HandlerBase):
    """
    Handler for retrieving price information from the Saxo Bank API.
    """
    
    def __init__(self, user_handler: UserHandler, session: Session, base_url: str, context_id: str) -> None:
        """
        Initialize the PriceHandler.

        Args:
            user_handler (UserHandler): The user handler with authentication information
            session (Session): The requests session
            base_url (str): The base URL for the Saxo Bank API
            context_id (str): The context ID for the API requests
        """
        super().__init__(session, base_url)
        self.user_handler = user_handler
        self.uic_cache: Dict[str, Dict[AssetType, int]] = {}  # Cache for symbol->UIC lookups
        self.context_id = context_id

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

    @functools.lru_cache(maxsize=128)
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
            
        except Exception as e:
            logger.error(f"Error getting UIC for {symbol}: {e}")
            return None
        if not data.get("Data"):
            logger.warning(f"No data found for symbol {symbol} and asset type {asset_type}.")
            return None
            
        if len(data["Data"]) > 1:
            # Try to find exact match
            items = [item for item in data["Data"] if item.get("Symbol").lower() == symbol.lower() and item.get("AssetType") == asset_type.value]
            if len(items) == 1:
                uic = items[0]["Identifier"]
            else:
                logger.warning(f"Multiple UICs found for symbol {symbol} and asset type {asset_type}.")
                for item in data["Data"]:
                    logger.warning(f"UIC: {item.get('Identifier')}, Symbol: {item.get('Symbol')}")
                # Use the first one as default
                uic = data[0]["Identifier"]
        elif len(data["Data"]) == 0:
            logger.warning(f"No UIC found for symbol {symbol} and asset type {asset_type}.")
            return None
        else:
            uic = data["Data"][0]["Identifier"]
        return uic
            

    def get_price_info_for_asset(self, uic: int, asset_type: AssetType) -> Optional[PriceInfo]:
        """
        Retrieves the price information for a single asset.

        Args:
            uic (int): The UIC of the asset
            asset_type (AssetType): The type of asset being queried

        Returns:
            Optional[PriceInfo]: The price information for the asset, or None if not found
        """
        price_info_list = self.get_price_info_for_assets([uic], asset_type)
        if not price_info_list:
            return None
        return price_info_list[0]

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
            
        except Exception as e:
            logger.error(f"Error getting price info for UICs {uics}: {e}")
            return []

        if not data.get("Data"):
            logger.warning(f"No price data found for UICs {uics} and asset type {asset_type}.")
            return []
            
        return [PriceInfo(price) for price in data["Data"]]
    @functools.lru_cache(maxsize=128)
    def get_price_increment_for_asset(self, uic: int, asset_type: AssetType, price: float = 0) -> Union[float, List[Dict[str, float]], None]:
        """
        Retrieves the price increment for a given asset.

        Args:
            uic (int): The UIC of the asset
            asset_type (AssetType): The type of asset being traded

        Returns:
            Union[float, List[Dict[str, float]], None]: The price increment or tick size schema, or None if not found or an error occurs
        """
        if price < 0:
            logger.error(f"Invalid price: {price}. Price must be non-negative.")
            return None

        try:
            url = (
                f"{self.base_url}/ref/v1/instruments/details/{uic}/{asset_type.value}"
                f"?AccountKey={self.user_handler.default_account_key}"
                f"&ClientKey={self.user_handler.client_key}"
            )
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.error(f"Error getting price increment for UIC {uic}: {e}")
            return None

        tick_schema = data.get('TickSizeScheme', {}).get('Elements', [])

        if not tick_schema:
            logger.warning(f"No tick size schema found for UIC {uic} and asset type {asset_type}.")
            return None
        if float(price) == 0:
            return tick_schema

        # Find the tick size that matches the price
        i = 0
        while price < tick_schema[i]['HighPrice']:
            i += 1

        if i >= len(tick_schema):
            logger.error(f"No matching tick size found for price {price} for UIC {uic} and asset type {asset_type}.")
            return None

        tick_size = tick_schema[i]['TickSize']
        return tick_size

    def is_valid_price(self, price: float, uic: int, asset_type: AssetType) -> bool:
        """
        Check if the given price is valid for the specified UIC and asset type.

        Args:
            price (float): The price to validate
            uic (int): The UIC of the asset
            asset_type (AssetType): The type of asset being traded

        Returns:
            bool: True if the price is valid, False otherwise
        """
        max_unit = 1000000
        tick_size = self.get_tick_size(price, uic, asset_type)
        if tick_size is None:
            logger.error(f"Failed to retrieve tick size for UIC {uic} and asset type {asset_type}.")
            return False
        if not isinstance(tick_size, (float, int)):
            logger.error(f"Expected tick size to be a float or int, got {type(tick_size)} for UIC {uic} and asset type {asset_type}.")
            return False

        return (price*max_unit) % (tick_size * max_unit) == 0

    def get_tick_size(self, price: float, uic: int, asset_type: AssetType) -> Optional[float]:
        """
        Get the tick size for a given price, UIC, and asset type.

        Args:
            price (float): The price of the asset
            uic (int): The UIC of the asset
            asset_type (AssetType): The type of asset being traded

        Returns:
            Optional[float]: The tick size for the asset or None if not found or an error occurs
        """
        tick_size = self.get_price_increment_for_asset(uic, asset_type) # Theres a better chance of the tick size schema being in cache than the tick size itself
        if tick_size is None:
            logger.error(f"Failed to retrieve tick size for UIC {uic} and asset type {asset_type}.")
            return None
        if not isinstance(tick_size, list):
            logger.error(f"Expected tick size schema to be a list, got {type(tick_size)} for UIC {uic} and asset type {asset_type}.")
            return None

        i = 0
        while i < len(tick_size) and price >= tick_size[i]['HighPrice']:
            i += 1
        if i >= len(tick_size):
            logger.error(f"No matching tick size found for price {price} for UIC {uic} and asset type {asset_type}.")
            return None
        tick_size = tick_size[i]['TickSize']

        return tick_size
