from flask import Blueprint
from routes import trade, account, price, subscription, health
import os
from streaming.clients import clients
from flask_sock import Sock

trade_bp = Blueprint("trade", __name__, url_prefix="/trade")
trade_bp.add_url_rule("/market_order", view_func=trade.create_market_order, methods=["POST", "GET", "OPTIONS"])  # type: ignore
trade_bp.add_url_rule("/orders", view_func=trade.get_orders, methods=["GET", "OPTIONS"])  # type: ignore


account_bp = Blueprint("account", __name__, url_prefix="/account")
account_bp.add_url_rule("/", view_func=account.get_account_info, methods=["GET", "OPTIONS"])  # type: ignore
account_bp.add_url_rule("/balance", view_func=account.get_balance, methods=["GET", "OPTIONS"])  # type: ignore
account_bp.add_url_rule("/positions", view_func=account.get_positions, methods=["GET", "OPTIONS"])  # type: ignore
if os.getenv("ENVIRONMENT") == "development":
    account_bp.add_url_rule("/reset", view_func=account.reset_account, methods=["POST", "OPTIONS"])  # type: ignore


price_bp = Blueprint("price", __name__, url_prefix="/price")
price_bp.add_url_rule("/<asset>/<asset_type>", view_func=price.get_single_price, methods=["GET", "OPTIONS"])  # type: ignore
price_bp.add_url_rule('/<asset>/<asset_type>/details', view_func=price.get_price_details, methods=['GET', 'OPTIONS'])  # type: ignore
price_bp.add_url_rule('/<asset>/<asset_type>/validate/<price>', view_func=price.validate_price, methods=['GET', 'OPTIONS'])  # type: ignore

subscription_bp = Blueprint("subscription", __name__, url_prefix="/subscription")
subscription_bp.add_url_rule("/", view_func=subscription.get_price_subscriptions, methods=["GET", "OPTIONS"])  # type: ignore
subscription_bp.add_url_rule("/<asset>/<asset_type>", view_func=subscription.price_subscription, methods=["POST", "OPTIONS"])  # type: ignore
subscription_bp.add_url_rule("/<reference_id>/<context_id>", view_func=subscription.price_subscription, methods=["DELETE", "OPTIONS"])  # type: ignore
subscription_bp.add_url_rule("/<context_id>", view_func=subscription.get_price_subscriptions, methods=["GET", "DELETE", "OPTIONS"])  # type: ignore

health_bp = Blueprint("health", __name__, url_prefix="/health")
health_bp.add_url_rule("/", view_func=health.health_check, methods=["GET", "OPTIONS"])  # type: ignore
health_bp.add_url_rule("/ready", view_func=health.ready_check, methods=["GET", "OPTIONS"])  # type: ignore

ws_bp = Blueprint("ws", __name__, url_prefix="/ws")
ws_sock = Sock(ws_bp)


@ws_sock.route("/all")
def ws_all(ws):
    clients.add_all(ws)
    try:
        while True:
            # keep the socket open; ignore inbound data
            try:
                _ = ws.receive(timeout=60)
            except Exception:
                pass
    finally:
        clients.remove_all(ws)


@ws_sock.route("/<ref_id>")
def ws_ref(ws, ref_id):
    clients.add_ref(ref_id, ws)
    try:
        while True:
            try:
                _ = ws.receive(timeout=60)
            except Exception:
                pass
    finally:
        clients.remove_ref(ref_id, ws)

def register_blueprints(app):
    """
    Register all blueprints with the Flask app.
    """
    app.register_blueprint(trade_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(price_bp)
    app.register_blueprint(subscription_bp)
    app.register_blueprint(health_bp)
    app.register_blueprint(ws_bp)

    def handle_error(message, status_code):
        """
        Handle errors and return a JSON response.
        """
        response = {"status": "error", "message": message, "status_code": status_code}
        return response, status_code

    @app.errorhandler(404)
    def not_found(error):
        """
        Handle 404 errors.
        """
        print(f"404 Error: {error}")
        return handle_error("Resource not found", 404)

    @app.errorhandler(500)
    def internal_server_error(error):
        """
        Handle 500 errors.
        """
        return handle_error("Internal server error", 500)

    @app.errorhandler(400)
    def bad_request(error):
        """
        Handle 400 errors.
        """
        return handle_error(error.description, 400)

    @app.errorhandler(401)
    def unauthorized(error):
        """
        Handle 401 errors.
        """
        return handle_error("Unauthorized", 401)

    @app.errorhandler(403)
    def forbidden(error):
        """
        Handle 403 errors.
        """
        return handle_error("Forbidden", 403)

    @app.errorhandler(405)
    def method_not_allowed(error):
        """
        Handle 405 errors.
        """
        return handle_error("Method not allowed", 405)

    @app.errorhandler(409)
    def conflict(error):
        """
        Handle 409 errors.
        """
        return handle_error("Conflict", 409)

    @app.errorhandler(422)
    def unprocessable_entity(error):
        """
        Handle 422 errors.
        """
        return handle_error("Unprocessable entity", 422)

    @app.errorhandler(429)
    def too_many_requests(error):
        """
        Handle 429 errors.
        """
        return handle_error("Too many requests", 429)

    @app.errorhandler(418)
    def teapot(error):
        """
        Handle 418 errors.
        """
        return handle_error("I am a teapot", 418)

    @app.errorhandler(415)
    def unsupported_media_type(error):
        """
        Handle 415 errors.
        """
        return handle_error("Unsupported media type", 415)
