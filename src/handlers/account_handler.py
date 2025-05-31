from handlers.handler_base import HandlerBase
from handlers.user_handler import UserHandler
from data_models.balance_information import BalanceInformation
from data_models.saxo.position import PositionModel
from data_models.saxo.historical_position import HistoricalPosition
from requests import Session
import logging

logger = logging.getLogger(__name__)

class AccountHandler(HandlerBase):
    """
    Handles account-related operations.
    """

    def __init__(self, session: Session, base_url: str, user_handler: UserHandler) -> None:
        """
        Initializes the AccountHandler with a session and base URL.

        Args:
            session (Session): The requests session to use for API calls.
            base_url (str): The base URL of the API.
        """
        super().__init__(session, base_url)
        self.base_url = base_url
        self.user_handler = user_handler
        self._account_key = self.user_handler.default_account_key
        self._client_key = self.user_handler.client_key

    def get_account_info(self) -> dict:
        """
        Retrieves account information.

        Args:
            account_key (str): The account key to retrieve information for.

        Returns:
            dict: The account information.
        """
        url = f"{self.base_url}/port/v1/accounts/{self._account_key}"
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Account info response: %s", response.text)
        return response.json()

    def get_account_balance(self) -> BalanceInformation:
        """
        Retrieves the account balance.

        Returns:
            dict: The account balance.
        """
        url = f"{self.base_url}/port/v1/balances?AccountKey={self._account_key}&ClientKey={self._client_key}"
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Account balance response: %s", response.text)
        return BalanceInformation(response.json()).cash_balance

    def get_account_balance_information(self) -> BalanceInformation:
        """
        Retrieves the account balance information.

        Returns:
            BalanceInformation: The account balance information.
        """
        url = f"{self.base_url}/port/v1/balances?AccountKey={self._account_key}&ClientKey={self._client_key}"
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Account balance information response: %s", response.text)
        return BalanceInformation(response.json())

    def _get_next_page(self, url: str) -> list:
        """
        Helper function to get the next page of results.

        Args:
            url (str): The URL to fetch the next page from.

        Returns:
            dict: The response JSON.
        """
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Account positions next page response: %s", response.text)
        data: list = response.json()["Data"]
        if response.json().get("__next", None):
            next_url = response.json()["__next"]
            return data + self._get_next_page(next_url)

        return data


    def get_account_positions(self) -> list:
        """
        Retrieves the account positions.

        Returns:
            dict: The account positions.
        """
        url = f"{self.base_url}/port/v1/positions?AccountKey={self._account_key}&ClientKey={self._client_key}"
        
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Account positions response: %s", response.text)
        json = response.json()
        data = json.get("Data", [])
        if json.get("__next", None):
            next_url = json.get("__next")
            data += self._get_next_page(next_url)
        return [PositionModel(item) for item in data]

    def get_historical_positions(self) -> list:
        """
        Retrieves historical positions for the account.

        Args:
            start (str): The start date in ISO format.
            end (str): The end date in ISO format.

        Returns:
            list: The historical positions.
        """
        url = f"{self.base_url}/port/v1/closedpositions?AccountKey={self._account_key}&ClientKey={self._client_key}&StandardPeriod=Year"
        response = self.session.get(url)
        response.raise_for_status()
        logger.debug("Response: %s", response.text)
        json = response.json()
        if isinstance(json, list):
            logger.warning("Received a list instead of a dict while getting historical positions - returning empty list.")
            return []
        logger.debug("Historical positions response: %s", json)
        return [HistoricalPosition(item) for item in json.get("Data", [])]
