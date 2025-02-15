from saxo_client import SaxoClient
from urllib.parse import urljoin


class Diagnostics:
    def __init__(self, client: SaxoClient):
        self.client = client

    def get(self):
        return self.client.session.get(urljoin(self.client.base_url, "root/v1/diagnostics/get"))

    def post(self):
        return self.client.session.post(urljoin(self.client.base_url, "root/v1/diagnostics/post"))

    def put(self):
        return self.client.session.put(urljoin(self.client.base_url, "root/v1/diagnostics/put"))

    def delete(self):
        return self.client.session.delete(urljoin(self.client.base_url, "root/v1/diagnostics/delete"))

    def patch(self):
        return self.client.session.patch(urljoin(self.client.base_url, "root/v1/diagnostics/patch"))

    def options(self):
        return self.client.session.options(urljoin(self.client.base_url, "root/v1/diagnostics/options"))

    def head(self):
        return self.client.session.head(urljoin(self.client.base_url, "root/v1/diagnostics/head"))

    def check_health(self):
        assert self.get().status_code == 200
