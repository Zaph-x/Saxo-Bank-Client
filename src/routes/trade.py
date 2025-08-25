from flask import request, abort
from dependency_injector.wiring import inject, Provide
from container import Container
from saxo_client import SaxoClient
from data_models.trade_payload import MarketOrderTradePayload
from jsonschema.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


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
        logger.debug("Received request method: %s", request.method)
        logger.debug("SaxoClient can_trade: %s", saxo_client.can_trade)
        if not saxo_client.can_trade:
            abort(403, "Trading is not allowed at the moment.")
        if not request.is_json:
            abort(415, "Request must be in JSON format.")
        logger.debug("Request is JSON formatted.")
        data = request.get_json()
        logger.debug("Received JSON data: %s", data)
        if not data:
            abort(400, "Request body cannot be empty.")
        try:
            # Validate and create TradePayload object
            trade_payload = MarketOrderTradePayload.from_json(data)
            logger.debug("Trade payload created: %s", trade_payload)
            response = saxo_client.trade_handler.place_market_order(trade_payload)
            logger.debug("Response from place_market_order: %s", response)

            if not response:
                abort(500, "Failed to create market order.")

            return {
                "status": "success",
                "order_id": response["OrderId"],
                "message": "Market order created successfully.",
                "status_code": 201,
            }


        except ValueError as e:
            # Handle validation errors
            logger.error("Validation error: %s", e)
            return {"status": "error", "message": str(e), "status_code": 400}
        except ValidationError as e:
            # Handle JSON schema validation errors
            logger.error("JSON schema validation error: %s", e)
            return {"status": "error", "message": str(e), "status_code": 400}
        except Exception as e:
            # Handle other exceptions
            logger.error("Unexpected error: %s", e)
            return {"status": "error", "message": "An unexpected error occurred.", "status_code": 500}

    if request.method == "POST":
        return handle_POST()
    elif request.method == "OPTIONS":
        return {
            "status": "success",
            "allowed_methods": "POST, OPTIONS",
            "message": "CORS preflight response",
            "status_code": 200,
        }

@inject
def get_orders(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Get the list of orders.

    Returns:
        dict: A dictionary containing order details.
    """

    # Placeholder for order retrieval logic
    def handle_GET():
        """
        Handle GET request for retrieving orders.
        """
        if not saxo_client.account_handler:
            abort(403, "Account handler is not available.")

        orders = saxo_client.trade_handler.get_all_orders()
        if not orders:
            abort(404, "No orders found.")

        return {
            "status": "success",
            "orders": [order.to_json() for order in orders],
            "status_code": 200,
        }

    if request.method == "GET":
        return handle_GET()
    elif request.method == "OPTIONS":
        return {
            "status": "success",
            "allowed_methods": "GET, OPTIONS",
            "message": "CORS preflight response",
            "status_code": 200,
        }
