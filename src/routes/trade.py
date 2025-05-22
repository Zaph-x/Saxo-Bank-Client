from flask import request, abort
from dependency_injector.wiring import inject, Provide
from container import Container
from saxo_client import SaxoClient
from data_models.trade_payload import MarketOrderTradePayload
from jsonschema.exceptions import ValidationError


@inject
def create_market_order(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Create a new trade.

    Returns:
        dict: A dictionary containing trade details.
    """

    # Placeholder for trade creation logic
    def handle_POST():
        """
        Handle POST request for creating a market order.
        """
        breakpoint()
        if not saxo_client.can_trade:
            abort(403, "Trading is not allowed at the moment.")
        if not request.is_json:
            abort(415, "Request must be in JSON format.")
        data = request.get_json()
        if not data:
            abort(400, "Request body cannot be empty.")
        try:
            # Validate and create TradePayload object
            trade_payload = MarketOrderTradePayload.from_json(data)

        except ValueError as e:
            # Handle validation errors
            return {"status": "error", "message": str(e), "status_code": 400}
        except ValidationError as e:
            # Handle JSON schema validation errors
            return {"status": "error", "message": str(e), "status_code": 400}

    if request.method == "POST":
        handle_POST()
    elif request.method == "OPTIONS":
        return {
            "status": "success",
            "allowed_methods": "POST, INFO, OPTIONS",
            "message": "CORS preflight response",
            "status_code": 200,
        }
    elif request.method == "INFO":
        # Explain GET and POST methods with example payloads
        return {
            "status": "success",
            "allowed_methods": "POST, GET, OPTIONS",
            "message": "GET and POST methods explained with example payloads",
            "post_example": {
                "payload": {
                    "symbol": "XAUUSD",
                    "quantity": 10,
                    "side": "long",
                    "sl_tp": {"sl": {"price": 50, "type": "pip"}, "tp": {"price": 100, "type": "pip"}},
                },
                "response": {"order_id": "123456"},
                "description": "Create a market order for 10 units of XAUUSD with a stop loss of 50 pips and take profit of 100 pips.",
            },
            "status_code": 200,
        }
        pass
