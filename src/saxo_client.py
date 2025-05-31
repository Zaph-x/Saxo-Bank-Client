import requests
import logging
from typing import Optional
import os
from handlers.user_handler import UserHandler
from handlers.account_handler import AccountHandler
from handlers.trade_handler import TradeHandler
from handlers.price_handler import PriceHandler
from data_models.response_models import UserModel
from redis import Redis
from redis.client import PubSub
import threading

logger = logging.getLogger(__name__)


class SaxoClient:
    """This class is used to authenticate with the Saxo OpenAPI and manage the session.
    It handles the OAuth2 authentication flow and token management.
    """

    user_handler: Optional[UserHandler] = None
    price_handler: Optional[PriceHandler] = None
    redis_channel: str = "oauth_access_token"
    access_token: Optional[str] = None

    def __init__(self: "SaxoClient", redis: Redis, interactive: bool = False) -> None:
        self.base_url = os.getenv("BASE_URL", "https://gateway.saxobank.com/sim/openapi")
        self.redis = redis
        self.session = requests.Session()
        self.interactive = interactive
        self.channel = self.redis.pubsub()
        logger.debug(f"Redis channel: {self.redis_channel}")
        logger.debug(f"Redis host: {self.redis.connection_pool.connection_kwargs['host']}")
        self.channel.subscribe(self.redis_channel)
        self.redis_thread = threading.Thread(target=self._listen_for_token, args=(self.channel,))
        self.redis_thread.daemon = True
        self.redis_thread.start()
        self.set_token(str(redis.get(self.redis_channel)))
        self.set_up_handlers()

    def set_up_handlers(self: "SaxoClient") -> None:
        """This method sets up the user, account, trade, and price handlers.
        It should be called after the user is authenticated.

        Example:
            >>> saxo_client.set_up_handlers()
        """
        self.user_handler = UserHandler(self.session, self.base_url)
        self.account_handler = AccountHandler(self.session, self.base_url, self.user_handler)
        self.trade_handler = TradeHandler(self.user_handler, self.session, self.base_url)
        self.price_handler = PriceHandler(self.user_handler, self.session, self.base_url)

    def set_token(self: "SaxoClient", token: str) -> None:
        """This method sets the access token for the session.
        It should be called after the user is authenticated.

        Args:
            token (str): The access token to set

        Example:
            >>> saxo_client.set_token("your_access_token")
        """
        self.access_token = token
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        logger.debug(f"Access token set: {self.access_token[:10]}...{self.access_token[-10:]}")

    def _listen_for_token(self: "SaxoClient", channel: PubSub) -> None:
        """This method listens for the access token from Redis.
        It should be called in a separate thread.

        Example:
            >>> saxo_client._listen_for_token(channel)
        """
        for message in channel.listen():
            if message["type"] == "message":
                self.access_token = str(message["data"])
                logger.debug(f"Received access token: {self.access_token[:10]}...{self.access_token[-10:]}")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})

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
