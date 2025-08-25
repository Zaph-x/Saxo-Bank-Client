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
def get_price_subscriptions(context_id: str, saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Get all price subscriptions.

    Returns:
        dict: A dictionary containing the list of price subscriptions.
    """

    def handle_GET():
        """
        Handle GET request for retrieving all price subscriptions.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")

        subscriptions = saxo_client.subscription_handler.get_price_subscriptions()
        if not subscriptions:
            return ApiResponse(
                status_code=200,
                message="No price subscriptions found.",
                subscriptions=[]
            )

        return ApiResponse(
            status_code=200,
            message="Price subscriptions retrieved successfully.",
            subscriptions=[humps.camelize(sub) for sub in subscriptions]
        )

    def handle_DELETE():
        """
        Handle DELETE request for removing all price subscriptions.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")

        tag = request.args.get('tag', None)  # Optional tag parameter, not used in this context

        result = saxo_client.subscription_handler.remove_all_price_subscriptions(context_id, tag)

        if result is None:
            abort(500, "Failed to remove all price subscriptions.")
        if not result:
            return ApiResponse(
                status_code=404,
                message="No price subscriptions found to remove."
            )
        logger.info("All price subscriptions removed successfully.")
       
        return ApiResponse(
            status_code=200,
            message="All price subscriptions removed successfully."
        )

    logger.debug("Received request method: %s", request.method)
    if request.method == "GET":
        return handle_GET()
    elif request.method == "DELETE":
        return handle_DELETE()
    elif request.method == "OPTIONS":
        return ApiResponse(
            status_code=200,
            message="CORS preflight response",
            allowed_methods="GET, DELETE, OPTIONS"
        )

    return ApiResponse(
        status_code=405,
        message="Method not allowed. Use GET to retrieve or DELETE to remove price subscriptions."
    )

@inject
def price_subscription(asset: str = "", asset_type: str = "", reference_id: str = "", context_id: str = "", saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """
    Create a price subscription for a given asset.

    Args:
        asset (str): The asset identifier.

    Returns:
        dict: A dictionary containing the subscription details.
    """
    def handle_DELETE():
        """
        Handle DELETE request for removing a price subscription for an asset.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")
        if not reference_id or not context_id:
            abort(400, "Reference ID and context ID are required for deletion.")

        result = saxo_client.subscription_handler.remove_price_subscription(
            context_id=context_id,
            reference_id=reference_id
        )
        if result is None:
            abort(500, f"Failed to remove price subscription for asset '{asset}'.")
        return ApiResponse(
            status_code=200,
            message=f"Price subscription for {reference_id} in {context_id} removed successfully."
        )

    def handle_POST():
        """
        Handle POST request for creating a price subscription for an asset.
        """
        if not saxo_client.price_handler:
            abort(403, "Price handler is not available.")
        if not asset:
            abort(400, "Asset identifier is required.")
        context_id = request.json.get("context_id", "default_context")
        if not context_id:
            abort(400, "Context ID is required.")
        algo_name = request.json.get("algo_name")
        if not algo_name:
            abort(400, "Algorithm name is required.")

        result = saxo_client.subscription_handler.create_price_subscription(
            asset=asset,
            asset_type=AssetType(asset_type),
            context_id=context_id,
            algo_name=algo_name,
            timeframe=request.json.get("timeframe", 1000)  # Default to 1000 ms if not provided
        )
        if result is None:
            abort(500, f"Failed to create price subscription for asset '{asset}'.")
        return ApiResponse(
            status_code=201,
            message=f"Price subscription for asset {asset_type} '{asset}' created successfully.",
            subscription_id=result
        )

    if request.method == "POST":
        return handle_POST()
    elif request.method == "DELETE":
        return handle_DELETE()
    elif request.method == "OPTIONS":
        return ApiResponse(
            status_code=200,
            message="CORS preflight response",
            allowed_methods="POST, OPTIONS"
        )

    return ApiResponse(
        status_code=405,
        message="Method not allowed. Use POST to create a price subscription."
    )

