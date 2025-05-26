from flask import request, abort
from dependency_injector.wiring import inject, Provide
from container import Container
from saxo_client import SaxoClient
import logging
import humps

logger = logging.getLogger(__name__)

@inject
def get_balance(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Get the account balance.

    Returns:
        dict: A dictionary containing account balance details.
    """

    # Placeholder for balance retrieval logic
    def handle_GET():
        """
        Handle GET request for retrieving account balance.
        """

        if not saxo_client.account_handler:
            abort(403, "Account handler is not available.")

        balance = saxo_client.account_handler.get_account_balance_information()
        if balance is None:
            abort(404, "Account balance not found.")

        return humps.decamelize({
            "status": "success",
            "balance": balance.to_json(),
            "status_code": 200,
        })

    logger.debug("Received request method: %s", request.method)
    if request.method == "GET":
        return handle_GET()
    elif request.method == "OPTIONS":
        return {
            "status": "success",
            "allowed_methods": "GET, OPTIONS",
            "message": "CORS preflight response",
            "status_code": 200,
        }

@inject
def get_positions(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Get the account positions.

    Returns:
        dict: A dictionary containing account positions details.
    """

    # Placeholder for positions retrieval logic
    def handle_GET():
        """
        Handle GET request for retrieving account positions.
        """

        if not saxo_client.account_handler:
            abort(403, "Account handler is not available.")

        positions = saxo_client.account_handler.get_account_positions()
        if positions is None:
            abort(404, "Account positions not found.")

        historical_positions = saxo_client.account_handler.get_historical_positions()
        if historical_positions is None:
            abort(404, "Historical positions not found.")

        # Assuming positions is a list of dictionaries
        pos = [pos.to_json() for pos in positions]
        return humps.decamelize({
            "status": "success",
            "positions": {
                "positions": pos,
                "count": len(pos),
            },
            "historical_positions": {
                "positions": [pos.to_json() for pos in historical_positions],
                "count": len(historical_positions),
            },
            "status_code": 200,
        })

    if request.method == "GET":
        return handle_GET()
    elif request.method == "OPTIONS":
        return {
            "status": "success",
            "allowed_methods": "GET, OPTIONS",
            "message": "CORS preflight response",
            "status_code": 200,
        }
