from requests import Session
from data_models.response_models import UserModel
from handlers.handler_base import HandlerBase


class UserHandler(HandlerBase):
    def __init__(self, session: Session, base_url: str) -> None:
        super().__init__(session, base_url)
        self.client_info: dict = {}

    def get_user(self) -> UserModel:
        response = self.session.get(f"{self.base_url}/root/v2/user")
        response.raise_for_status()
        return UserModel.from_json(response.json())

    def _get_client_info(self) -> None:
        if self.client_info:
            return
        response = self.session.get(f"{self.base_url}/port/v1/clients/me")
        response.raise_for_status()
        self.client_info = response.json()

    @property
    def default_currency(self) -> str:
        if self.client_info:
            return self.client_info["DefaultCurrency"]
        self._get_client_info()
        return self.client_info["DefaultCurrency"]

    @property
    def default_account_key(self) -> str:
        if self.client_info:
            return self.client_info["DefaultAccountKey"]
        self._get_client_info()
        return self.client_info["DefaultAccountKey"]

    @property
    def client_key(self) -> str:
        if self.client_info:
            return self.client_info["ClientKey"]
        self._get_client_info()
        return self.client_info["ClientKey"]

    @property
    def legal_assets(self) -> list:
        if self.client_info:
            return self.client_info["LegalAssetTypes"]
        self._get_client_info()
        return self.client_info["LegalAssetTypes"]
