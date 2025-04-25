import requests
import random
import threading
import string
import logging
import webbrowser
from auth.server import AuthServer
from data_models import AppConfig, TokenDataModel
from typing import Optional
import time
from handlers.user_handler import UserHandler
from handlers.account_handler import AccountHandler
from handlers.trade_handler import TradeHandler
from data_models.response_models import UserModel
from redis import Redis

logger = logging.getLogger(__name__)


class SaxoClient:
    """This class is used to authenticate with the Saxo OpenAPI and manage the session.
    It handles the OAuth2 authentication flow and token management.
    """

    user_handler: Optional[UserHandler] = None
    redis_channel: str = "oauth_access_token"

    def __init__(self: "SaxoClient", app_config: AppConfig, redis: Redis, interactive: bool = False) -> None:

        self.base_url = app_config.open_api_base_url

        self.session = requests.Session()
        self.interactive = interactive

    def ensure_success(self: "SaxoClient", response: requests.Response, failure_message: str = "") -> None:
        if int(response.status_code / 100) not in (2, 3):
            logger.error("Request failed with status code " + str(response.status_code))
            if failure_message:
                logger.error(failure_message)
            logger.error("Response: " + response.text)
            exit(1)

    @staticmethod
    def _new_state(string_length: int = 16) -> str:
        return "".join(random.choices(string.ascii_letters + string.digits, k=string_length))

    def _periodic_refresh(self: "SaxoClient", interval: int) -> None:
        logger.debug("Refreshing token")
        token_data = self._refresh_token()
        threading.Timer(interval, self._periodic_refresh, [token_data.expires_in - 10]).start()

    def _refresh_token(self: "SaxoClient") -> TokenDataModel:
        response = requests.post(
            self.app_config.token_endpoint,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "redirect_uri": self.app_config.redirect_urls[0],
                "client_id": self.app_config.app_key,
                "client_secret": self.app_config.app_secret,
            },
        )
        self.ensure_success(response, "Failed to refresh token")
        token_data = TokenDataModel.from_json(response.json())
        logger.debug("Got " + str(token_data))
        self.session.headers.update({"Authorization": "Bearer " + token_data.access_token})
        self.refresh_token = token_data.refresh_token
        logger.debug("Token refreshed. Starting new timer for " + str(token_data.expires_in) + " seconds")
        if self.redis:
            self.redis.set("saxo_token_data", token_data.to_json())
            logger.debug("Saved token data to Redis")
            self.redis.set("saxo_state", self.state)
            logger.debug("Saved state to Redis")
        return token_data

    def wait_for_code(self: "SaxoClient") -> str:
        counter = 0
        if AuthServer.get_code() == "":
            logger.info("Waiting for code...")
            while AuthServer.get_code() == "" and counter < 120:
                time.sleep(1)
                logger.debug("Waiting 1 second for code...")
                counter += 1
        if counter >= 120:
            logger.error("Failed to authenticate after 2 minutes")
            exit(1)
        logger.debug("Authenticated with code " + AuthServer.get_code())
        return AuthServer.code

    def get_token(self: "SaxoClient") -> TokenDataModel:
        response = requests.post(
            self.app_config.token_endpoint,
            data={
                "grant_type": "authorization_code",
                "code": AuthServer.get_code(),
                "redirect_uri": self.app_config.redirect_urls[0],
                "client_id": self.app_config.app_key,
                "client_secret": self.app_config.app_secret,
            },
        )
        self.ensure_success(response, "Failed to get token")
        token_data = TokenDataModel.from_json(response.json())
        logger.debug("Got " + str(token_data))
        return token_data

    def authenticate(self: "SaxoClient") -> None:

        response = requests.get(
            self.app_config.authorization_endpoint,
            params={
                "response_type": "code",
                "client_id": self.app_config.app_key,
                "redirect_uri": self.app_config.redirect_urls[0],
                "state": self.state,
            },
        )
        self.ensure_success(response, "Failed to get authorization code")
        self.await_authentication(response.url)
        token_data = self.get_token()
        self.session.headers.update({"Authorization": "Bearer " + token_data.access_token})
        self.create_and_start_refresh_thread(token_data)
        self.set_up_handlers()
        logger.info("Authenticated")

    def logout(self: "SaxoClient") -> None:
        self.refrehs_thread.cancel()
        logger.info("Logged out")

    def await_authentication(self: "SaxoClient", signin_url) -> None:
        """This method waits for the user to authenticate.
        It should be called after the user is authenticated.

        Example:
            >>> saxo_client.await_authentication()
        """
        webbrowser.open(signin_url)
        self.auth_server.start_server()
        thread = threading.Thread(target=self.wait_for_code)
        thread.start()
        thread.join()
        self.auth_server.stop_server()

    def set_up_handlers(self: "SaxoClient") -> None:
        """This method sets up the user, account, and trade handlers.
        It should be called after the user is authenticated.

        Example:
            >>> saxo_client.set_up_handlers()
        """
        self.user_handler = UserHandler(self.session, self.base_url)
        self.account_handler = AccountHandler(self.session, self.base_url, self.user_handler)
        self.trade_handler = TradeHandler(self.user_handler, self.session, self.base_url)

    def create_and_start_refresh_thread(self, token_data: TokenDataModel) -> None:
        """This method creates a thread to refresh the token periodically.
        It should be called after the user is authenticated.

        Args:
            token_data (TokenDataModel): The token data model object

        Example:
            >>> saxo_client.create_and_start_refresh_thread(token_data)
        """
        self.refresh_token = token_data.refresh_token
        logger.debug("Starting timer for " + str(token_data.expires_in) + " seconds")
        self.refrehs_thread = threading.Timer(
            token_data.expires_in - 20, self._periodic_refresh, [token_data.expires_in - 10]
        )
        self.refrehs_thread.start()

    @property
    def can_trade(self: "SaxoClient") -> bool:
        """This method returns True if the user is authenticated and can trade.
        It returns False if the user is not authenticated or cannot trade.

        Returns:
            bool: True if the user can trade, False otherwise

        Example:
            >>> can_trade = saxo_client.can_trade
            >>> print(can_trade)
            True
        """
        if self.user_handler is None:
            logger.warning("User handler is not initialized. Cannot check if user can trade.")
            return False
        return True

    @property
    def user(self: "SaxoClient") -> Optional[UserModel]:
        """This method returns the user object of the authenticated user.
        It returns None if the user is not authenticated.

        Returns:
            Optional[UserModel]: The user object of the authenticated user

        Example:
            >>> user = saxo_client.user
            >>> print(user)
            UserModel
        """
        if self.user_handler is None:
            logger.warning("User handler is not initialized. Cannot get user.")
            return None
        return self.user_handler.get_user()
