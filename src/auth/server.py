"""
This is the authentication server that will be used to receive the redirect from Saxo Bank.
This server is a simple HTTP server that listens on a configurable port (Default: 5000) and has a single endpoint /redirect.
The server starts its own thread and runs in the background.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from socketserver import ThreadingMixIn
from threading import Thread
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        sender = self.client_address[0]
        if sender != "127.0.0.1":  # Only allow requests from localhost
            self.reject_request()
            return
        if path == "/redirect":
            query = urlparse(self.path).query
            query_components = parse_qs(query)
            try:
                self.send_body(
                    b"<html><head><title>Authentication Successful</title></head>"
                    + b"<body><h1>Authentication Successful</h1><br><h3>This page can now be closed</h3></body>"
                    + b"</html>"
                )
                AuthServer.set_code(query_components["code"][0])
            except Exception as e:
                self.send_body(
                    (
                        b"<html><head><title>Authentication Failed</title></head>"
                        + b"<body><h1>Authentication Failed</h1></body></html>"
                    ),
                    status_code=500,
                )
                logger.error(e)

    def reject_request(self):
        self.send_body(
            b"<html><head><title>Forbidden</title></head><body><h1>Forbidden</h1></body></html>", status_code=403
        )

    def send_body(self, body, status_code: int = 200, headers: dict = {"Content-type": "text/html"}):
        self.send_response(status_code)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        if isinstance(body, bytes):
            self.wfile.write(body)
        else:
            self.wfile.write(body.encode("utf-8"))

    def log_message(self, format, *args):
        logger.debug("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), format % args))


class AuthServer(ThreadingMixIn, HTTPServer):
    code: str = ""

    def __init__(
        self,
        client_id,
        client_secret,
        redirect_uri,
        server_address="0.0.0.0",
        RequestHandlerClass=RequestHandler,
        port=5000,
    ):
        super().__init__((server_address, port), RequestHandlerClass)
        self.client_id = client_id
        self.client_secret = client_secret
        if isinstance(redirect_uri, list):
            self.redirect_uri = [uri for uri in redirect_uri if urlparse(uri).port == port][0]
        elif isinstance(redirect_uri, str):
            self.redirect_uri = redirect_uri
        self.port = port
        self.server_thread = Thread(target=self.serve_forever)

    def start_server(self) -> None:
        logger.debug(f"Starting auth server on port {self.port}")
        try:
            self.server_thread.start()
        except KeyboardInterrupt:
            self.stop_server()

    def stop_server(self) -> None:
        logger.debug("Stopping auth server")
        self.shutdown()
        self.server_thread.join()

    @staticmethod
    def get_code() -> str:
        return AuthServer.code or ""

    @staticmethod
    def set_code(code: str) -> None:
        AuthServer.code = code


def run_auth_server(client_id: str, client_secret: str, redirect_uri: str, port: int = 5000):
    server = AuthServer(client_id, client_secret, redirect_uri, port=port)
    server.start_server()
