from objects.client_configuration import ClientConfiguration
import argparse
import logging
from flask import Flask
from container import Container
from urls import register_blueprints


def parse_args():
    parser = argparse.ArgumentParser(description="Saxo API Client")
    parser.add_argument(
        "--loglevel",
        type=str,
        help="Logging level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive (debug) mode with breakpoint.",
    )
    parser.add_argument(
        "--redis-host",
        type=str,
        help="Redis host. This overrides the config file setting and will fetch the token data from Redis.",
        default="localhost",
    )
    parser.add_argument(
        "--redis-port",
        type=int,
        help="Redis port.",
        default=6379,
    )
    parser.add_argument(
        "--redis-db",
        type=int,
        help="Redis database number.",
        default=0,
    )
    return parser.parse_args()


def create_app():
    """Create a Flask application."""
    container = Container()
    container.init_resources()
    container.wire(modules=["routes.trade"])
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.container = container  # pyright: ignore[reportAttributeAccessIssue]

    register_blueprints(app)
    return app


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    client_config = ClientConfiguration(
        redis_host=args.redis_host,
        redis_port=args.redis_port,
        redis_db=args.redis_db,
    )

    if args.interactive:
        from saxo_client import SaxoClient
        from redis import StrictRedis

        client = SaxoClient(
            StrictRedis(
                host=args.redis_host, port=args.redis_port, db=args.redis_db, decode_responses=True, encoding="utf-8"
            )
        )
        breakpoint()

    app = create_app()

    app.run(debug=args.loglevel.upper() == "DEBUG")
