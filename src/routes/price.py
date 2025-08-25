from flask import request, abort
from dependency_injector.wiring import inject, Provide
from container import Container
from saxo_client import SaxoClient
from objects import ApiResponse
import logging
import humps
from data_models.trading.asset_type import AssetType

logger = logging.getLogger(__name__)

@inject
def get_single_price(asset: str, asset_type: str, saxo_client: SaxoClient = Provide[Container.saxo_client]):
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
        try:
            _asset_type = AssetType(asset_type)
        except ValueError:
            abort(400, f"Invalid asset type: {asset_type}")

        price = saxo_client.price_handler.get_price(asset, _asset_type)
        if price is None:
            abort(404, f"Price for asset '{asset}' not found.")

        return ApiResponse(
            status_code=200,
            message=f"Price for asset {asset_type} '{asset}' retrieved successfully.",
            price=price.to_json()
        )

    logger.debug("Received request method: %s", request.method)
    if request.method == "GET":
        return handle_GET()
    elif request.method == "OPTIONS":
        return ApiResponse(
            status_code=200,
            message="CORS preflight response",
            allowed_methods="GET, OPTIONS"
        )

@inject
def validate_price(asset: str, asset_type: str, price: float, saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Validate the price of a single asset.

    Args:
        asset (str): The asset identifier.

    Returns:
        dict: A dictionary containing the validation result.
    """

    def handle_GET():
        """
        Handle GET request for validating the price of a single asset.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")
            
        try:
            _asset_type = AssetType(asset_type)
        except ValueError:
            abort(400, f"Invalid asset type: {asset_type}")

        uic = saxo_client.price_handler.get_uic_for_symbol(asset, _asset_type)

        if uic is None:
            abort(404, f"UIC for asset '{asset}' not found.")

        is_valid = saxo_client.price_handler.is_valid_price(price, uic, _asset_type)
        return ApiResponse(
            status_code=200,
            message=f"Price validation for asset {asset_type} '{asset}' completed.",
            is_valid=is_valid
        )

    logger.debug("Received request method: %s", request.method)
    if request.method == "GET":
        return handle_GET()
    elif request.method == "OPTIONS":
        return ApiResponse(
            status_code=200,
            message="CORS preflight response",
            allowed_methods="GET, OPTIONS"
        )

@inject
def get_price_details(asset: str, asset_type: str, saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Get the price details of a single asset.

    Args:
        asset (str): The asset identifier.

    Returns:
        dict: A dictionary containing the asset price details.
    """

    def handle_GET():
        """
        Handle GET request for retrieving the price details of a single asset.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")
            
        # Get asset_type from request args, default to Stock if not provided
        try:
            _asset_type = AssetType(asset_type)
        except ValueError:
            abort(400, f"Invalid asset type: {asset_type}")

        uic = saxo_client.price_handler.get_uic_for_symbol(asset, _asset_type)
        if uic is None:
            abort(404, f"UIC for asset '{asset}' not found.")
        price_increment = saxo_client.price_handler.get_price_increment_for_asset(uic, _asset_type)
        price_info = saxo_client.price_handler.get_price_info_for_assets([uic], _asset_type)

        if price_increment is None:
            abort(404, f"Price for asset '{asset}' not found.")

        return ApiResponse(
            status_code=200,
            message=f"Price details for asset {asset_type} '{asset}' retrieved successfully.",
            price_details={
                "uic": uic,
                "price_increment": price_increment,
                "price_info": price_info[0].to_json() if price_info else None
            }
        )

    logger.debug("Received request method: %s", request.method)
    if request.method == "GET":
        return handle_GET()
    elif request.method == "OPTIONS":
        return ApiResponse(
            status_code=200,
            message="CORS preflight response",
            allowed_methods="GET, OPTIONS"
        )

