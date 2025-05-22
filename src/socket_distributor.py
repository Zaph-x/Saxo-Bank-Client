import asyncio
import threading
import struct
import json
import uuid
import logging
import requests
import websockets


class SocketDistributor:
    def __init__(self, session, subscription_url, socket_url):
        self.session = session
        self.subscription_url = subscription_url
        self.socket_url = socket_url
        self.context_id = str(uuid.uuid4())
        self.subscriptions = {}
        self.socket = None
        self.ref_to_uic = {}
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_event_loop, daemon=True).start()

    def add_subscriber(self, uic, asset_type, callback):
        if uic not in self.subscriptions:
            ref_id = f"uic_{uic}"
            self.subscriptions[uic] = {"ref_id": ref_id, "last_message": None, "subscribers": set()}
            self.ref_to_uic[ref_id] = uic
            self.loop.call_soon_threadsafe(asyncio.create_task, self._subscribe(uic, ref_id, asset_type))
        self.subscriptions[uic]["subscribers"].add(callback)

    def remove_subscriber(self, uic, callback):
        if uic in self.subscriptions:
            self.subscriptions[uic]["subscribers"].discard(callback)
            if not self.subscriptions[uic]["subscribers"]:
                logging.info(f"Unsubscribing from {uic}")

    async def _subscribe(self, uic, ref_id, asset_type):
        url = f"{self.subscription_url}?context_id={self.context_id}"
        body = (
            {"Arguments": {"AssetType": asset_type, "Uic": uic}, "ContextId": self.context_id, "ReferenceId": ref_id},
        )
        try:
            response = self.session.post(url, json=body)
            if response.status_code == 201:
                logging.info(f"Subscribed to {uic}")
            else:
                logging.error(f"Failed to subscribe to {uic}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Request failed: {e}")

    def _unsubscribe(self, uic):
        url = f"{self.subscription_url}?context_id={self.context_id}"

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._main())

    async def _connect_to_socket(self):
        headers = [(k, v) for k, v in self.session.headers.items()]
        self.websocket = await websockets.connect(
            f"{self.socket_url}?context_id={self.context_id}",
            extra_headers=headers,
        )
        logging.info("Connected to saxo socket")

    async def _receive_messages(self):
        try:
            async for message in self.websocket:
                if isinstance(message, bytes):
                    await self._process_message(message)
        except Exception as e:
            logging.error(f"Error receiving message: {e}")

    async def _process_message(self, message: bytes):
        try:
            offset = 0
            message_id = struct.unpack_from("<Q", message)[0]
            offset += 8
            offset += 2
            ref_id_size = struct.unpack_from("<B", message, offset)[0]
            offset += 1
            ref_id = message[offset : offset + ref_id_size].decode("utf-8")
            offset += ref_id_size
            offset += 1
            payload_size = struct.unpack_from("<I", message, offset)[0]
            offset += 4
            payload = message[offset : offset + payload_size].decode("utf-8")
            parsed_payload = json.loads(payload)

            message_obj = {"message_id": message_id, "ref_id": ref_id, "payload": parsed_payload}

            await self._broadcast_message(message_obj)
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    async def _broadcast_message(self, message_obj):
        uic = self.ref_to_uic.get(message_obj["ref_id"])
        if not uic:
            return
        self.subscriptions[uic]["last_message"] = message_obj
        for subscribers in self.subscriptions[uic]["subscribers"]:
            try:
                await subscribers(message_obj)
            except Exception as e:
                logging.error(f"Error broadcasting message to subscriber: {e}")

    async def _main(self):
        await self._connect_to_socket()
        await self._receive_messages()
