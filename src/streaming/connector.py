import websocket
import json
import asyncio


class SaxoWebsocketConnector:
    ws: websocket.WebSocket

    def __init__(self, token, client_key, client_secret):
        self.token = token
        self.client_key = client_key
        self.client_secret = client_secret
        self._connect()

    def _connect(self):
        self.ws = websocket.create_connection(
            f"wss://gateway.saxobank.com/sim/openapi/streamingws/connect?authorization=Bearer {self.token}&contextId=1"
        )

    def subscribe(self, data):
        self.ws.send(json.dumps(data))

    def unsubscribe(self, data):
        self.ws.send(json.dumps(data))

    def get_data(self):
        return self.ws.recv()

    def close(self):
        self.ws.close()

    def __del__(self):
        self.close()
