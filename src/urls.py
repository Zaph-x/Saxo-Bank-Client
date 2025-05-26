from flask import Blueprint
from routes import trade
from routes import account

trade_bp = Blueprint("trade", __name__, url_prefix="/trade")
trade_bp.add_url_rule("/market_order", view_func=trade.create_market_order, methods=["POST", "GET", "INFO", "OPTIONS"])  # type: ignore
trade_bp.add_url_rule("/orders", view_func=trade.get_orders, methods=["GET", "OPTIONS"])  # type: ignore


account_bp = Blueprint("account", __name__, url_prefix="/account")
account_bp.add_url_rule("/balance", view_func=account.get_balance, methods=["GET", "OPTIONS"])  # type: ignore
account_bp.add_url_rule("/positions", view_func=account.get_positions, methods=["GET", "OPTIONS"])  # type: ignore


def register_blueprints(app):
    """
    Register all blueprints with the Flask app.
    """
    app.register_blueprint(trade_bp)
    app.register_blueprint(account_bp)

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
        return handle_error("Bad request", 400)

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
