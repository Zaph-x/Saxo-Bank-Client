import json
import time
import struct
import eventlet
from websocket import WebSocketApp  # websocket-client
from typing import Any, Dict, Generator
import logging

logger = logging.getLogger(__name__)

class Upstream:
    """Maintains one upstream connection to Saxo and fans out messages via Clients."""

    def __init__(self, url: str, token: str, context_id: str, clients) -> None:
        self.url = f"{url}?contextId={context_id}&authorization=Bearer%20{token}"
        self.token = token
        self.clients = clients
        self.ws: WebSocketApp | None = None
        self.backoff = 1.0
        self.max_backoff = 15.0

    def start(self) -> None:
        logger.info(f"Starting upstream connection to {self.url[:50]}...")
        logger.debug(f"Using token: {self.token[:10]}...{self.token[-10:]}")
        eventlet.spawn_n(self._run_loop)

    @staticmethod
    def decode_ws_msg(raw: (bytes)) -> Generator[Dict[str, Any], None, None]:
        """Binary frame → messages (compatible with your tested dummy)."""
        while raw:
            (msgIdentifier,), raw = struct.unpack_from("Q", raw[:8]), raw[8 + 2:]
            (Srefid,), raw = struct.unpack_from("B", raw[:1]), raw[1:]
            (refid_bytes,), raw = struct.unpack_from(f"{Srefid}s", raw[:Srefid]), raw[Srefid:]
            (payloadFmt,), raw = struct.unpack_from("B", raw[:1]), raw[1:]
            (payloadSize,), raw = struct.unpack_from("i", raw[:4]), raw[4:]
            (payload,) = struct.unpack_from(f"{payloadSize}s", raw[:payloadSize])

            refid = refid_bytes.decode("utf-8")
            msg: Dict[str, Any] = {"refid": refid, "msgId": msgIdentifier}
            if payloadFmt == 0:
                msg["msg"] = json.loads(payload.decode("utf-8"))
            else:
                try:
                    msg["msg"] = payload.decode("utf-8")
                except Exception:
                    msg["msg"] = payload.hex()
            raw = raw[payloadSize:]
            yield msg

    def _on_open(self, _ws) -> None:
        logger.info(f"Upstream connected")
        self.backoff = 1.0

    def _on_message(self, _ws, message: Any) -> None:
        logger.debug(f"Upstream message received: {type(message)} {len(message) if hasattr(message, '__len__') else ''}")
        try:
            for m in self.decode_ws_msg(message):
                logger.debug(f"Decoded message: {m}")
                self.clients.push_all(message)
                self.clients.push_ref(m.get("refid", ""), message)
        except Exception as e:
            logger.warning("Error handling message: %s", e)

        # Optional: reset handling for JSON path
        try:
            if not isinstance(message, (bytes, bytearray)):
                obj = json.loads(message)
                if obj.get("Reset") or obj.get("ResetRequired") or obj.get("Reason") == "Reset":
                    try:
                        _ws.close()
                    except Exception:
                        pass
        except Exception:
            pass

    def _on_error(self, _ws, error: Any) -> None:
        logger.error("Upstream error:", error)

    def _on_close(self, _ws, status_code: Any, msg: Any) -> None:
        logger.warning("Upstream closed:", status_code, msg)

    def _run_loop(self) -> None:
        logger.debug("Starting upstream connection loop")
        headers = [f"Authorization: Bearer {self.token}"]
        while True:
            self.ws = WebSocketApp(
                self.url,
                header=headers,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            try:
                self.ws.run_forever(ping_interval=20, ping_timeout=10, ping_payload="ping")
                # TODO handle re-authentication if needed
            except Exception as e:
                logger.error("run_forever failed:", e)

            delay = self.backoff
            self.backoff = min(self.backoff * 2.0, self.max_backoff)
            logger.info(f"Backoff delay: {delay:.1f}s")
            eventlet.sleep(delay)

