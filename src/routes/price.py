from flask import request, abort
from dependency_injector.wiring import inject, Provide
from container import Container
from saxo_client import SaxoClient
import logging
import humps
from data_models.trading.asset_type import AssetType

logger = logging.getLogger(__name__)

@inject
def get_single_price(asset: str, saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Get the price of a single asset.

    Args:
        asset (str): The asset identifier.

    Returns:
        dict: A dictionary containing the asset price details.
    """

    def handle_GET():
        """
        Handle GET request for retrieving the price of a single asset.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")
            
        # Get asset_type from request args, default to Stock if not provided
        asset_type_str = request.args.get('asset_type', 'Stock')
        try:
            asset_type = AssetType(asset_type_str)
        except ValueError:
            abort(400, f"Invalid asset type: {asset_type_str}")

        price = saxo_client.price_handler.get_price(asset, asset_type)
        if price is None:
            abort(404, f"Price for asset '{asset}' not found.")

        return humps.decamelize({
            "status": "success",
            "price": price.to_json(),
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
