import requests
import random
import threading
import string
import logging
import webbrowser
from auth.server import AuthServer
from models.token_data import TokenDataModel
from models.app_config import AppConfig
from models import AppConfig, TokenDataModel, UserModel
from typing import Optional
import time

logger = logging.getLogger(__name__)


class SaxoClient:
    def __init__(self: "SaxoClient", app_config: AppConfig):
        self.app_config = app_config
        self.base_url = app_config.open_api_base_url

        self.state = self._new_state()
        self.auth_server = AuthServer(
            app_config.app_key, app_config.app_secret, app_config.redirect_urls[0], port=44315
        )
        self.session = requests.Session()

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
        if response.status_code != 200:
            logger.error("Failed to authenticate")
            return

        webbrowser.open(response.url)
        self.auth_server.start_server()
        thread = threading.Thread(target=self.wait_for_code)
        thread.start()
        thread.join()
        self.auth_server.stop_server()
        token_data = self.get_token()
        self.session.headers.update({"Authorization": "Bearer " + token_data.access_token})
        self.refresh_token = token_data.refresh_token
        logger.debug("Starting timer for " + str(token_data.expires_in) + " seconds")
        self.refrehs_thread = threading.Timer(token_data.expires_in - 20, self._periodic_refresh, [token_data.expires_in - 10])
        self.refrehs_thread.start()
        logger.info("Authenticated")

    def logout(self: "SaxoClient") -> None:
        self.refrehs_thread.cancel()
        logger.info("Logged out")

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
        if "Authorization" not in self.session.headers:
            logger.error("Not authenticated")
            return None
        response = self.session.get(self.base_url + "/root/v2/user")
        self.ensure_success(response, "Failed to get user")
        return UserModel.from_json(response.text)
