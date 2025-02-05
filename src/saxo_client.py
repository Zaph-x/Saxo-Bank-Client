import requests
import random
import threading
import string
import os
import logging
import webbrowser
from auth.server import AuthServer
import time

logger = logging.getLogger(__name__)


class SaxoClient:

    def __init__(self: "SaxoClient", app_config: dict):
        self._validate_self(app_config)
        self.app_config = app_config
        self.base_url = app_config["OpenApiBaseUrl"]

        self.state = self._new_state()
        self.auth_server = AuthServer(app_config["AppKey"], app_config["AppSecret"], app_config["RedirectUrls"], port=self.config_item("port", 44315))
        self.session = requests.Session()

    def ensure_success(self: "SaxoClient", response: requests.Response, failure_message: str = "") -> None:
        if int(response.status_code / 100) not in (2,3):
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
        threading.Timer(interval, self._periodic_refresh, [self.expires_in - 10]).start()
        self._refresh_token()

    def _refresh_token(self: "SaxoClient") -> None:
        response = requests.post(
            str(self.config_item("TokenEndpoint")),
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "redirect_uri": self.config_item("RedirectUrls"),
                "client_id": self.config_item("AppKey"),
                "client_secret": self.config_item("AppSecret"),
            },
        )
        self.ensure_success(response, "Failed to refresh token")
        token_data = response.json()
        logger.debug("Got token data " + str(self.redact_token_data(token_data)))
        self.access_token = token_data.get("access_token", "")
        self.refresh_token = token_data.get("refresh_token", "")
        self.expires_in = token_data.get("expires_in", 0)
        self.session.headers.update({"Authorization": "Bearer " + self.access_token})
        logger.debug("Token refreshed. Starting new timer for " + str(self.expires_in) +" seconds")


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

    def get_token(self: "SaxoClient") -> dict:
        response = requests.post(
            str(self.config_item("TokenEndpoint")),
            data={
                "grant_type": "authorization_code",
                "code": AuthServer.get_code(),
                "redirect_uri": self.config_item("RedirectUrls"),
                "client_id": self.config_item("AppKey"),
                "client_secret": self.config_item("AppSecret"),
            },
        )
        self.ensure_success(response, "Failed to get token")
        logger.debug("Got token data " + str(self.redact_token_data(response.json())))
        return response.json()

    def authenticate(self: "SaxoClient") -> None:
        response = requests.get(
            str(self.config_item("AuthorizationEndpoint")),
            params={
                "response_type": "code",
                "client_id": self.config_item("AppKey"),
                "redirect_uri": self.config_item("RedirectUrls"),
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
        self.access_token = token_data.get("access_token", "")
        self.refresh_token = token_data.get("refresh_token", "")
        self.expires_in = token_data.get("expires_in", 0)
        self.session.headers.update({"Authorization": "Bearer " + self.access_token})
        self._periodic_refresh(self.expires_in - 10)

    def _validate_self(self: "SaxoClient", config: dict) -> None:
        def _isset(val: str, config: dict) -> bool:
            return val in config or os.getenv(val) is not None

        assert _isset("AppKey", config), "AppKey is required"
        assert _isset("AppSecret", config), "AppSecret is required"
        assert _isset("RedirectUrls", config), "RedirectUrls is required"
        assert _isset("AuthorizationEndpoint", config), "AuthorizationEndpoint is required"
        assert _isset("TokenEndpoint", config), "TokenEndpoint is required"
        assert _isset("OpenApiBaseUrl", config), "ApiEndpoint is required"
        assert _isset("GrantType", config), "GrantType is required"

    def redact_token_data(self: "SaxoClient", token_data: dict) -> dict:
        """Partially redact token data"""
        redacted_data = token_data.copy()
        redacted_data["access_token"] = redacted_data["access_token"][:5] + "[REDACTED]"
        redacted_data["refresh_token"] = redacted_data["refresh_token"][:5] + "[REDACTED]"
        return redacted_data

    def config_item(self: "SaxoClient", key: str, default=None) -> str | int | list | dict | None:
        if key in os.environ and os.environ.get(key) is not None:
            return os.environ.get(key, "") 
        return self.app_config[key] if key in self.app_config else default
