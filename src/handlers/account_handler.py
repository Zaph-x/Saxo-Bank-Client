from handlers.handler_base import HandlerBase
from handlers.user_handler import UserHandler
from data_models.balance_information import BalanceInformation
from requests import Session


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
        return BalanceInformation(response.json())
