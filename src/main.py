from dependency_injector.wiring import inject, Provide
from saxo_client import SaxoClient
from container import Container
import argparse
import logging
import os
from flask import Flask

logger = logging.getLogger(__name__)

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
        default="redis",
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


@inject
def create_client(saxo_client: SaxoClient = Provide[Container.saxo_client]):
    """Create a SaxoClient instance."""
    saxo_client.set_up_handlers()
    return saxo_client

def create_app(args):
    """Create a Flask application."""
    from container import Container
    from urls import register_blueprints
    container = Container()
    container.config.redis_host.from_env("REDIS_HOST", args.redis_host)
    container.config.redis_port.from_env("REDIS_PORT", args.redis_port)
    container.config.redis_db.from_env("REDIS_DB", args.redis_db)
    container.wire(modules=["routes.trade", "routes.account", __name__])
    logger.debug("Wired container with routes")
    logger.debug(f"Container: {container}")
    app = Flask(__name__)
    app.url_map.strict_slashes = False
    app.container = container  # pyright: ignore[reportAttributeAccessIssue]

    logger.info("Initialized container resources")
    register_blueprints(app)
    return app


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=os.getenv("LOGLEVEL", args.loglevel).upper())

    if args.interactive:
        from saxo_client import SaxoClient
        from redis import StrictRedis

        client = SaxoClient(
            StrictRedis(
                host=args.redis_host, port=args.redis_port, db=args.redis_db, decode_responses=True, encoding="utf-8"
            )
        )
        breakpoint()

    app = create_app(args)

    client = create_client()
    app.run(debug=args.loglevel.upper() == "DEBUG", host="0.0.0.0", port=5000)
